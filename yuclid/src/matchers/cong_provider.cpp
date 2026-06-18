#include "cong_provider.hpp"
#include "predicate_provider.hpp"
#include "mapping_state.hpp"
#include "lazy_geometry_cache.hpp"     
#include "rule_plan.hpp"
#include "geometry_cache_types.hpp"
#include "numbers/util.hpp"
#include "type/dist.hpp"
#include "statement/cong.hpp"

#include <unordered_map>
#include <cassert>

namespace Yuclid {
    namespace {
        std::array<std::size_t, 4> get_predicate_local_var_indexes(const PlannedPredicate &predicate) {
            std::array<std::size_t, 4> predicate_var_indexes;
            int next_unique_id = 0;
            for(int i = 0; i < 4; ++i){
                bool found = false;

                // Check if we have seen this string before
                for(int j = 0; j < i; ++j){
                    if(predicate.pattern.args[i] == predicate.pattern.args[j]){
                        // The variable is a duplicate! Give it the same index we gave the first one.
                        predicate_var_indexes[i] = predicate_var_indexes[j];
                        found = true;
                        break;
                    }
                }
                if(!found){
                    predicate_var_indexes[i] = next_unique_id;
                    next_unique_id++;
                }
            }
            return predicate_var_indexes;
        }

        std::array<std::optional<ProblemPointIndex>, 4> get_cong_assignments(
            const PlannedPredicate &predicate,
            const MappingState &mapping
        ) {
            std::array<std::optional<ProblemPointIndex>, 4> assignments;
            std::array<std::size_t, 4> local_predicate_indexes = get_predicate_local_var_indexes(predicate);

            for(int i = 0; i < 4; i++){
                assert(local_predicate_indexes[i] < predicate.variable_indices.size() 
                && "Cong provider ran into an issue, predicate-local varaible indexes indicate more unique variables than the planned predicate has.");

                // Get the optional point index for each variable. Map predicate-local variable indexes to the indexes of the variables in the schema.
                assignments[i] = mapping.assigned_point_index(predicate.variable_indices[local_predicate_indexes[i]]);
            }
            
            return assignments;
        }

        const std::vector<PointPairId>* get_bucket_for_key(
            const double key,
            const LazyGeometryCache &cache
        ) {
            const auto &all_point_pairs = cache.point_pairs();

            for (const auto &bucket : cache.segment_length_buckets().buckets) {
                // buckets are guaranteed to contain at least 2 elements
                double min_len = static_cast<double>(SquaredDist(cache.point(all_point_pairs[bucket.front()].first), cache.point(all_point_pairs[bucket.front()].second)));
                double max_len = static_cast<double>(SquaredDist(cache.point(all_point_pairs[bucket.back()].first), cache.point(all_point_pairs[bucket.back()].second)));
                
                if (key >= (min_len - EPS) && key <= (max_len + EPS)) {
                    return &bucket;
                }
            }

            return nullptr;
        }
    }

    // If one of the two segments is fully assigned, we can give the length of the bucket corresponding to its length
    // If theres a point and a segment, we will again return the bucket size to avoid unnecessary 
    // In the cases where theres nothing asssigned, only one point assigned, two points but not from the same segments 
    std::size_t CongProvider::estimate_extensions(
        const PlannedPredicate &predicate,
        const MappingState &mapping,
        const LazyGeometryCache &cache
    ) const {
        std::size_t estimate = 0;
        std::array<std::optional<ProblemPointIndex>, 4> assignments = get_cong_assignments(predicate, mapping);

        // Bitmask (A = bit 3, B = bit 2, C = bit 1, D = bit 0)
        uint8_t state_mask = 0;
        if (assignments[0].has_value()) state_mask |= 0b1000; // Variable A
        if (assignments[1].has_value()) state_mask |= 0b0100; // Variable B
        if (assignments[2].has_value()) state_mask |= 0b0010; // Variable C
        if (assignments[3].has_value()) state_mask |= 0b0001; // Variable D


        std::size_t total_pairs = cache.point_pairs().size();
        std::size_t num_buckets = cache.segment_length_buckets().buckets.size();
        // TODO: Decide on wether total_pairs is a good enough approximation for the sum of items in all buckets.
        std::size_t avg_bucket_size = (num_buckets == 0) ? 0 : (total_pairs / num_buckets);

        // When set to true, the estimate will be divided by cache.num_points() 
        bool intersect_estimates_with_point = false;

        switch (state_mask) {
            case 0b1111:
                // All 4 points assigned. No extensions to generate.
                estimate = 0;
                break;

            case 0b1110: // AB and C assigned, D free
            case 0b1101: // AB and D assigned, C free
            case 0b1011: // B free, A and CD assigned
            case 0b0111: // A free, B and CD assigned
                intersect_estimates_with_point = true;
                [[fallthrough]];
            case 0b1100: // AB assigned, CD free
            case 0b0011: // AB free, CD assigned
            {
                // The length is known! 
                double assigned_length = 0;
                if((state_mask & 0b1100) == 0b1100) {
                    assigned_length = static_cast<double>(SquaredDist(cache.point(*assignments[0]), cache.point(*assignments[1])));
                }
                else {
                    assigned_length = static_cast<double>(SquaredDist(cache.point(*assignments[2]), cache.point(*assignments[3]))); 
                }
                
                const auto bucket_ptr = get_bucket_for_key(assigned_length, cache);
                if(bucket_ptr != nullptr) {
                    // Extract one to exclude the already assigned segment
                    // Multiply by 2 because a segment XY can be mapped as XY or YX!
                    estimate = (bucket_ptr->size() - 1) * 2; 

                    if(intersect_estimates_with_point && cache.num_points() > 0) {
                        estimate = estimate / cache.num_points();
                        estimate = estimate > 0 ? estimate : 1;
                    }
                }

                break;
            }
            case 0b1010: case 0b1001: case 0b0110: case 0b0101:
                // Two points are known, but length is unknown.
                intersect_estimates_with_point = true;
                [[fallthrough]];
            case 0b1000: case 0b0100: case 0b0010: case 0b0001:
                // One point is known.
                // Assuming all segments that contain the point are in different buckets, than it appears in at most cache.num_points() - 1 buckets
                // The estimated extensions are therefore the number of buckets multiplied by the average length of a bucket 
                // Multiplied by 2 becase a segment can be mapped bidirectionally
                estimate = (cache.num_points() - 1) * avg_bucket_size * 2;

                if(intersect_estimates_with_point) {
                    estimate = estimate / cache.num_points();
                    estimate = estimate > 0 ? estimate : 1;
                }

                break;
        
            case 0b0000:
                // Every pair can be mapped in both directions
                estimate = cache.point_pairs().size() * 2;
                break;
        
            default:
                // All 16 cases are covered, this should never be reached
                break;
        }
        
        return predicate.metadata.base_cost + estimate;
    }

    std::generator<MappingExtension> CongProvider::generate_extensions(
        const PlannedPredicate &predicate,
        const MappingState &mapping,
        const LazyGeometryCache &cache
    ) const {
        std::array<std::optional<ProblemPointIndex>, 4> assignments = get_cong_assignments(predicate, mapping);
        std::array<std::size_t, 4> local_var_indexes = get_predicate_local_var_indexes(predicate);

        MappingExtension next_extension;
        const auto &all_point_pairs = cache.point_pairs();

        // Bitmask (A = bit 3, B = bit 2, C = bit 1, D = bit 0)
        uint8_t state_mask = 0;
        if (assignments[0].has_value()) state_mask |= 0b1000; // Variable A
        if (assignments[1].has_value()) state_mask |= 0b0100; // Variable B
        if (assignments[2].has_value()) state_mask |= 0b0010; // Variable C
        if (assignments[3].has_value()) state_mask |= 0b0001; // Variable D

        switch (state_mask) {
            // Case: All 4 points assigned. No extensions to generate.
            case 0b1111:
                co_return;
            
            // Case: 2 points assigned (the length is known)
            case 0b1100: // AB assigned, CD free
            case 0b0011: // AB free, CD assigned
            {
                bool is_ab_known = ((state_mask & 0b1100) == 0b1100);
                std::size_t var1_idx = local_var_indexes[is_ab_known ? 2 : 0];
                std::size_t var2_idx = local_var_indexes[is_ab_known ? 3 : 1];

                double assigned_length = static_cast<double>(SquaredDist(
                    cache.point(is_ab_known ? *assignments[0] : *assignments[2]), 
                    cache.point(is_ab_known ? *assignments[1] : *assignments[3])
                ));

                const auto bucket_ptr = get_bucket_for_key(assigned_length, cache);
                if(bucket_ptr != nullptr) {
                    for(PointPairId point_pair_id: *bucket_ptr){
                        const PointPair &pair = all_point_pairs[point_pair_id];

                        if(!mapping.is_point_used(pair.first) && !mapping.is_point_used(pair.second)) {
                            next_extension.clear_assignments();
                            next_extension.add_assignment(predicate.variable_indices[var1_idx], pair.first);
                            next_extension.add_assignment(predicate.variable_indices[var2_idx], pair.second);
                            co_yield next_extension;
                            
                            // Switch points
                            next_extension.clear_assignments();
                            next_extension.add_assignment(predicate.variable_indices[var1_idx], pair.second);
                            next_extension.add_assignment(predicate.variable_indices[var2_idx], pair.first);
                            co_yield next_extension;
                        }
                    }
                }
                break;
            }

            // Case: 3 Points assigned (Length Known, 1 to target)
            case 0b1110: case 0b1101: case 0b1011: case 0b0111:
            {
                // Find which variable is missing
                std::size_t missing_bit = (~state_mask) & 0b1111;
                std::size_t target_idx;
                double length;
                ProblemPointIndex anchor_point;
                
                if (missing_bit == 0b0001) { // D missing
                    target_idx = local_var_indexes[3];
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[0]), cache.point(*assignments[1])));
                    anchor_point = *assignments[2];
                } 
                else if (missing_bit == 0b0010) { // C missing
                    target_idx = local_var_indexes[2];
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[0]), cache.point(*assignments[1])));
                    anchor_point = *assignments[3];
                } 
                else if (missing_bit == 0b0100) { // B missing
                    target_idx = local_var_indexes[1];
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[2]), cache.point(*assignments[3])));
                    anchor_point = *assignments[0];
                } 
                else { // A missing
                    target_idx = local_var_indexes[0];
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[2]), cache.point(*assignments[3])));
                    anchor_point = *assignments[1];
                }

                const auto bucket_ptr = get_bucket_for_key(length, cache);
                if (bucket_ptr != nullptr) {
                    for (PointPairId id : *bucket_ptr) {
                        const PointPair &pair = all_point_pairs[id];
                        
                        // We strictly look for segments connected to our anchor point
                        if (pair.first == anchor_point && !mapping.is_point_used(pair.second)) {
                            next_extension.clear_assignments();
                            next_extension.add_assignment(predicate.variable_indices[target_idx], pair.second);
                            co_yield next_extension;
                        } 
                        else if (pair.second == anchor_point && !mapping.is_point_used(pair.first)) {
                            next_extension.clear_assignments();
                            next_extension.add_assignment(predicate.variable_indices[target_idx], pair.first);
                            co_yield next_extension;
                        }
                    }
                }
                break;
            }

            // Case: 1 Point Known (Length Unknown)
            case 0b1000: case 0b0100: case 0b0010: case 0b0001:
            {
                ProblemPointIndex anchor_point;
                std::size_t other_seg1_idx, seg2_idx_a, seg2_idx_b;

                // Pre-map the variable indices based on which point is known
                if (state_mask == 0b1000)      { anchor_point = *assignments[0]; other_seg1_idx = local_var_indexes[1]; seg2_idx_a = local_var_indexes[2]; seg2_idx_b = local_var_indexes[3]; }
                else if (state_mask == 0b0100) { anchor_point = *assignments[1]; other_seg1_idx = local_var_indexes[0]; seg2_idx_a = local_var_indexes[2]; seg2_idx_b = local_var_indexes[3]; }
                else if (state_mask == 0b0010) { anchor_point = *assignments[2]; other_seg1_idx = local_var_indexes[3]; seg2_idx_a = local_var_indexes[0]; seg2_idx_b = local_var_indexes[1]; }
                else                          { anchor_point = *assignments[3]; other_seg1_idx = local_var_indexes[2]; seg2_idx_a = local_var_indexes[0]; seg2_idx_b = local_var_indexes[1]; }

                for (const auto &bucket : cache.segment_length_buckets().buckets) {
                    // Find all segments in this bucket that touch our anchor point
                    for (PointPairId id1 : bucket) {
                        const PointPair &pair1 = all_point_pairs[id1];
                        
                        ProblemPointIndex matching_other_end;
                        if (pair1.first == anchor_point) matching_other_end = pair1.second;
                        else if (pair1.second == anchor_point) matching_other_end = pair1.first;
                        else continue; // Doesn't touch our anchor, skip

                        if (mapping.is_point_used(matching_other_end)) continue;

                        // Combine this valid pair with every other pair in the same bucket
                        for (PointPairId id2 : bucket) {
                            if (id1 == id2) continue; // Don't match the segment with itself
                            const PointPair &pair2 = all_point_pairs[id2];
                            
                            if (!mapping.is_point_used(pair2.first) && !mapping.is_point_used(pair2.second)) {
                                next_extension.clear_assignments();
                                next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end);
                                next_extension.add_assignment(predicate.variable_indices[seg2_idx_a], pair2.first);
                                next_extension.add_assignment(predicate.variable_indices[seg2_idx_b], pair2.second);
                                co_yield next_extension;

                                next_extension.clear_assignments();
                                next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end);
                                next_extension.add_assignment(predicate.variable_indices[seg2_idx_a], pair2.second);
                                next_extension.add_assignment(predicate.variable_indices[seg2_idx_b], pair2.first);
                                co_yield next_extension;
                            }
                        }
                    }
                }
                break;
            }
            
            // Case: 2 Independent Points Known (Similar to previous case)
            case 0b1010: // A and C assigned
            case 0b1001: // A and D assigned
            case 0b0110: // B and C assigned
            case 0b0101: // B and D assigned
            {
                ProblemPointIndex anchor_seg1, anchor_seg2;
                std::size_t other_seg1_idx, other_seg2_idx;

                // Pre-map the variable indices based on which point is known
                if (state_mask == 0b1010)      { anchor_seg1 = *assignments[0]; other_seg1_idx = local_var_indexes[1]; anchor_seg2 = *assignments[2]; other_seg2_idx = local_var_indexes[3]; }
                else if (state_mask == 0b1001) { anchor_seg1 = *assignments[0]; other_seg1_idx = local_var_indexes[1]; anchor_seg2 = *assignments[3]; other_seg2_idx = local_var_indexes[2]; }
                else if (state_mask == 0b0110) { anchor_seg1 = *assignments[1]; other_seg1_idx = local_var_indexes[0]; anchor_seg2 = *assignments[2]; other_seg2_idx = local_var_indexes[3]; }
                else                          { anchor_seg1 = *assignments[1]; other_seg1_idx = local_var_indexes[0]; anchor_seg2 = *assignments[3]; other_seg2_idx = local_var_indexes[2]; }

                for (const auto &bucket : cache.segment_length_buckets().buckets) {
                    // Find all segments in this bucket that touch the first anchor point
                    for (PointPairId id1 : bucket) {
                        const PointPair &pair1 = all_point_pairs[id1];
                        
                        ProblemPointIndex matching_other_end_seg_1;
                        if (pair1.first == anchor_seg1) matching_other_end_seg_1 = pair1.second;
                        else if (pair1.second == anchor_seg1) matching_other_end_seg_1 = pair1.first;
                        else continue; // Doesn't touch our anchor, skip

                        if (mapping.is_point_used(matching_other_end_seg_1)) continue;

                        // Combine this valid pair with every pair in the same bucket that touches the second anchor
                        for (PointPairId id2 : bucket) {
                            if (id1 == id2) continue; // Don't match the segment with itself
                            const PointPair &pair2 = all_point_pairs[id2];

                            ProblemPointIndex matching_other_end_seg_2;
                            if (pair2.first == anchor_seg2) matching_other_end_seg_2 = pair2.second;
                            else if (pair2.second == anchor_seg2) matching_other_end_seg_2 = pair2.first;
                            else continue; // Doesn't touch our anchor, skip
                            
                            // Skip if point is already used
                            if (mapping.is_point_used(matching_other_end_seg_2)) continue;

                            // --- THE ALIAS CONTRACT ---
                            if (other_seg1_idx == other_seg2_idx) {
                                // These have the same variable index, so they are the same vairable(e.g., cong A B A C). 
                                // Therefore, the discovered points must be the same as well!
                                if (matching_other_end_seg_1 != matching_other_end_seg_2) continue;
                            
                                // Avoid assigning the same variable twice
                                next_extension.clear_assignments();
                                next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end_seg_1);
                                co_yield next_extension;
                            } 
                            else {
                                // The two variables have different indexes (e.g., cong A B C D).
                                // Therefore, the points must be different as well.
                                if (matching_other_end_seg_1 == matching_other_end_seg_2) continue;
                            
                                // Assign both
                                next_extension.clear_assignments();
                                next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end_seg_1);
                                next_extension.add_assignment(predicate.variable_indices[other_seg2_idx], matching_other_end_seg_2);
                                co_yield next_extension;
                            }
                        }
                    }
                }
                break;
            }
            
            // Case: 0 Points Known (Brute Force Combinations)
            case 0b0000:
            {
                for (const auto &bucket : cache.segment_length_buckets().buckets) {
                    if (bucket.size() < 2) continue;

                    for (size_t i = 0; i < bucket.size(); ++i) {
                        for (size_t j = i + 1; j < bucket.size(); ++j) {
                            const PointPair &p1 = all_point_pairs[bucket[i]];
                            const PointPair &p2 = all_point_pairs[bucket[j]];

                            if (mapping.is_point_used(p1.first) || mapping.is_point_used(p1.second) ||
                                mapping.is_point_used(p2.first) || mapping.is_point_used(p2.second)) continue;

                            // Yield 4 directional permutations (AB->CD, AB->DC, BA->CD, BA->DC)
                            for (int swap_state = 0; swap_state < 4; ++swap_state) {
                                ProblemPointIndex pt_a = (swap_state & 1) ? p1.second : p1.first;
                                ProblemPointIndex pt_b = (swap_state & 1) ? p1.first : p1.second;
                                ProblemPointIndex pt_c = (swap_state & 2) ? p2.second : p2.first;
                                ProblemPointIndex pt_d = (swap_state & 2) ? p2.first : p2.second;

                                // --- Variable repetition check ---
                                // If the variable indices are equal, the points must be equal.
                                // If the variable indices are NOT equal, the points mut NOT be equal.
                                bool valid = true;
                                if ((local_var_indexes[0] == local_var_indexes[1]) != (pt_a == pt_b)) valid = false;
                                if ((local_var_indexes[0] == local_var_indexes[2]) != (pt_a == pt_c)) valid = false;
                                if ((local_var_indexes[0] == local_var_indexes[3]) != (pt_a == pt_d)) valid = false;
                                if ((local_var_indexes[1] == local_var_indexes[2]) != (pt_b == pt_c)) valid = false;
                                if ((local_var_indexes[1] == local_var_indexes[3]) != (pt_b == pt_d)) valid = false;
                                if ((local_var_indexes[2] == local_var_indexes[3]) != (pt_c == pt_d)) valid = false;

                                if (!valid) continue;

                                next_extension.clear_assignments();

                                // We keep track of what we've added to avoid double-assigning aliases
                                uint8_t added_mask = 0; 

                                // Helper lambda to avoid assigning the same variable more than once
                                auto safe_add = [&](std::size_t idx, ProblemPointIndex pt) {
                                    if ((added_mask & (1 << idx)) == 0) {
                                        next_extension.add_assignment(predicate.variable_indices[idx], pt);
                                        added_mask |= (1 << idx);
                                    }
                                };
                            
                                safe_add(local_var_indexes[0], pt_a);
                                safe_add(local_var_indexes[1], pt_b);
                                safe_add(local_var_indexes[2], pt_c);
                                safe_add(local_var_indexes[3], pt_d);
                            
                                co_yield next_extension;
                            }
                        }
                    }
                }
                break;
            }
        
            default: break;
        }
        
        co_return;
    }

    bool CongProvider::is_satisfied(
        const PlannedPredicate &predicate,
        const MappingState &mapping,
        const LazyGeometryCache &cache
    ) const {
        std::array<std::optional<ProblemPointIndex>, 4> assignments = get_cong_assignments(predicate, mapping);

        // Failsafe
        if (!assignments[0].has_value() || !assignments[1].has_value() || 
            !assignments[2].has_value() || !assignments[3].has_value()) {
            return false;
        }

        DistEqDist cong_statement(
            Dist(cache.point(*assignments[0]), cache.point(*assignments[1])),
            Dist(cache.point(*assignments[2]), cache.point(*assignments[3]))
        );

        return cong_statement.check_nondegen() && cong_statement.check_equations();
    }

}