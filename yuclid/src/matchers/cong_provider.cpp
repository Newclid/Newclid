#include "cong_provider.hpp"
#include "predicate_provider.hpp"
#include "mapping_state.hpp"
#include "lazy_geometry_cache.hpp"     
#include "rule_plan.hpp"
#include "geometry_cache_types.hpp"
#include "numbers/util.hpp"
#include "type/dist.hpp"
#include "statement/cong.hpp"

#include <cassert>

namespace Yuclid {
    namespace {
        // TODO: Planned predicate: Save the indeces of all variables in order
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

        // TODO: Cache This is a temporary replacement, once a key is added to the segment buckets, remove this
        const std::vector<PointPairId>* get_bucket_for_key(
            const double key,
            const LazyGeometryCache &cache
        ) {
            const auto &all_point_pairs = cache.point_pairs();

            for (const auto &bucket : cache.segment_length_buckets().buckets) {
                // buckets are guaranteed to contain at least 2 elements
                double min_len = static_cast<double>(SquaredDist(cache.point(all_point_pairs[bucket.front()].first), cache.point(all_point_pairs[bucket.front()].second)));
                double max_len = static_cast<double>(SquaredDist(cache.point(all_point_pairs[bucket.back()].first), cache.point(all_point_pairs[bucket.back()].second)));
                
                // Inclusive lower and exclusive upper boundary, shouldn't be a concern generally, but still, it should resolve the potential bucket overlap issue.
                if (key >= (min_len - EPS) && key < (max_len + EPS)) {
                    return &bucket;
                }
            }

            return nullptr;
        }
        
        // Pairwise variable check
        // If variables are the same, points must be the same. 
        // If variables are different, points must be different.
        inline bool check_var_equality(std::size_t var1, std::size_t var2, ProblemPointIndex pt1, ProblemPointIndex pt2) {
            return (var1 == var2) == (pt1 == pt2);
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
        assert(predicate.pattern.args.size() == 4);
        std::size_t estimate = 0;
        std::array<std::optional<ProblemPointIndex>, 4> assignments = get_cong_assignments(predicate, mapping);

        // Bitmask (A = bit 3, B = bit 2, C = bit 1, D = bit 0)
        // This mask determines exactly which geometric state we are evaluating.
        uint8_t state_mask = 0;
        if (assignments[0].has_value()) state_mask |= 0b1000; // Variable A
        if (assignments[1].has_value()) state_mask |= 0b0100; // Variable B
        if (assignments[2].has_value()) state_mask |= 0b0010; // Variable C
        if (assignments[3].has_value()) state_mask |= 0b0001; // Variable D


        // TODO: Cache: Add average number of elements in buckets
        std::size_t total_pairs = cache.point_pairs().size();
        std::size_t num_buckets = cache.segment_length_buckets().buckets.size();
        // TODO: Decide on wether total_pairs is a good enough approximation for the sum of items in all buckets.
        std::size_t avg_bucket_size = (num_buckets == 0) ? 0 : (total_pairs / num_buckets);

        // Flag to apply the "Intersection Reduction". If we know an independent point, 
        // When we know at least one specific point (e.g., A is already bound to Point #5), 
        // the number of valid geometric combinations is reduced significantly. 
        //
        // Take a problem with 100 points and 500 segments inside the buckets. If we pick a segment completely 
        // at random, the odds that it specifically touches Point #5 are roughly 2 / 100.
        // 
        // If 'intersect_estimates_with_point' is true, it means our search state is strictly 
        // anchored to a known point. Thats why we divide the raw combinations by the total number of points in 
        // the problem (later would be changed to the total number of points inside the buckets). 
        // This simulates the probability of a random segment actually intersecting our known anchor point.
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
                    // Subtract 1 to exclude the segment we already know
                    // Multiply by 2 because a segment XY can be mapped as XY or YX!
                    estimate = (bucket_ptr->size() - 1) * 2; 

                    if(intersect_estimates_with_point && cache.num_points() > 0) {
                        // We apply the intersection reduction described above
                        // We enforce a minimum estimate of 1 (estimate > 0 ? estimate : 1)
                        // We use Ceiling Division: (estimate + N - 1) / N.
                        // This reduces the margin of error in our estimation.
                        // An example of how the error is reduced - Take a problem wtih 20 points. 
                        // The estimate computed up to this point is the estimate for branches before intersecting with a concrete point.
                        // If we dont use ceiling division, a case with 1 branch and a case with 39 branches, will both result in an estimate of 1.
                        // With ceiling division, cases from 1 - 20 branches result in an estimate of 1, and those with 21 - 40 branches result in an estimate of 2
                        std::size_t N = cache.num_points();
                        estimate = (estimate + N - 1) / N;
                        
                        // Failsafe: Ensure we never return 0 cost for cases that can map a value
                        estimate = estimate > 0 ? estimate : 1;
                    }
                }

                break;
            }
            case 0b1010: case 0b1001: case 0b0110: case 0b0101:
                // Two disconnected points known (e.g., A and C). Apply heavy intersection reduction.
                intersect_estimates_with_point = true;
                [[fallthrough]];
            case 0b1000: case 0b0100: case 0b0010: case 0b0001:
            {
                // One point is known.
                // Heuristics guess: One point is known, length is unknown.
                // We assume the known point connects to (Total Points - 1) other points.
                // We assume each of those segments belongs to a distinct bucket of average size.
                // We multiply by 2 because each segment can be mapped bidirectionally
                std::size_t connections = cache.num_points() > 0 ? cache.num_points() - 1 : 0;
                estimate = connections * avg_bucket_size * 2;

                if(intersect_estimates_with_point && cache.num_points() > 0) {
                    // We apply the intersection reduction described above
                    // The logic is similar to the one desribed in the previous cases.
                    std::size_t N = cache.num_points();
                    estimate = (estimate + N - 1) / N;
                    
                    // Failsafe: Ensure we never return 0 cost for cases that can map a value
                    estimate = estimate > 0 ? estimate : 1;
                }

                break;
            }
            case 0b0000:
                // Brute force combinations: No points known.
                // Combinatorics: For each bucket of size S, we pick 2 segments.
                // Any segment for the first pair (S choices).
                // Any segment for the second pair (S choices).
                // Note: We allow picking the same segment twice (S * S) because the rule 
                // might be an identity alias like `cong A B A B`. If it's not an identity rule, 
                // the generator's variable check will filter it out, but S * S is the upper bound.
                // 
                // For each pair, we yield 4 directional permutations (XY->ZW, XY->WZ, YX->ZW, YX->WZ).
                // Total yield per bucket = 4 * S * S.
                estimate = num_buckets * (avg_bucket_size * avg_bucket_size * 4);
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
        assert(predicate.pattern.args.size() == 4);
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


        // ----------------------------------------------------------------------
        // THE TAUTOLOGY FAST-PATH (Identity Maps)
        // ----------------------------------------------------------------------
        // If the rule is `cong A B A B` or `cong A B B A`, it is mathematically 
        // true for ALL segments. Because the cache buckets skip "singleton" segments,
        // relying on the bucket loops would cause us to silently drop valid singletons.
        // To fix this, if we detect an identity map, we bypass the buckets entirely.
        // ----------------------------------------------------------------------
        bool is_identity = 
            (local_var_indexes[0] == local_var_indexes[2] && local_var_indexes[1] == local_var_indexes[3]) ||
            (local_var_indexes[0] == local_var_indexes[3] && local_var_indexes[1] == local_var_indexes[2]);

        if (is_identity) {
            // If it's an identity, and we have 0 points bound (0b0000), just yield ALL point pairs.
            if (state_mask == 0b0000) {
                for (const PointPair &pair : all_point_pairs) {
                    if (mapping.is_point_used(pair.first) || mapping.is_point_used(pair.second)) continue;

                    next_extension.clear_assignments();
                    // No need to map 2 and 3, they are the exact same variables
                    next_extension.add_assignment(predicate.variable_indices[local_var_indexes[0]], pair.first);
                    next_extension.add_assignment(predicate.variable_indices[local_var_indexes[1]], pair.second);
                    co_yield next_extension;

                    next_extension.clear_assignments();
                    next_extension.add_assignment(predicate.variable_indices[local_var_indexes[0]], pair.second);
                    next_extension.add_assignment(predicate.variable_indices[local_var_indexes[1]], pair.first);
                    co_yield next_extension;
                }
                co_return;
            }
            
            // If it's an identity and 1 point is bound (e.g., A is known, state 0b1010),
            // just loop all points and yield the remaining free variable!
            if (state_mask == 0b1010 || state_mask == 0b1001 || state_mask == 0b0110 || state_mask == 0b0101) {
                ProblemPointIndex known_pt = assignments[0].has_value() ? *assignments[0] : *assignments[1];
                std::size_t missing_var_idx = assignments[0].has_value() ? local_var_indexes[1] : local_var_indexes[0];

                for (ProblemPointIndex p = 0; p < cache.num_points(); ++p) {
                    if (p != known_pt && !mapping.is_point_used(p)) {
                        next_extension.clear_assignments();
                        next_extension.add_assignment(predicate.variable_indices[missing_var_idx], p);
                        co_yield next_extension;
                    }
                }
                co_return;
            }
            co_return;
        }

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
                            if (!check_var_equality(var1_idx, var2_idx, pair.first, pair.second)) continue;

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
                // state_mask represents what we know (e.g., 0b1110 means A,B,C known, D missing).
                // By inverting the mask (~state_mask), the missing '0' becomes a '1'.
                std::size_t missing_bit = (~state_mask) & 0b1111;
                std::size_t target_idx;
                double length;
                ProblemPointIndex anchor_point;
                
                if (missing_bit == 0b0001) { // D missing
                    // D is missing. We know A, B, and C.
                    target_idx = local_var_indexes[3];
                    // We know the length because A and B are fully bound.
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[0]), cache.point(*assignments[1])));
                    // Since C is known, the new segment must connect to C. C is our anchor.
                    anchor_point = *assignments[2];
                } 
                else if (missing_bit == 0b0010) { // C missing
                    target_idx = local_var_indexes[2];
                    // We know the length because A and B are fully bound.
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[0]), cache.point(*assignments[1])));
                    // Since D is known, the new segment must connect to D. D is our anchor.
                    anchor_point = *assignments[3];
                } 
                else if (missing_bit == 0b0100) { // B missing
                    target_idx = local_var_indexes[1];
                    // We know the length because C and D are fully bound.
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[2]), cache.point(*assignments[3])));
                    // Since A is known, the new segment must connect to A. A is our anchor.
                    anchor_point = *assignments[0];
                } 
                else { // A missing
                    target_idx = local_var_indexes[0];
                    // We know the length because C and D are fully bound.
                    length = static_cast<double>(SquaredDist(cache.point(*assignments[2]), cache.point(*assignments[3])));
                    // Since B is known, the new segment must connect to B. B is our anchor.
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

                // ---------------------------------------------------------------------------------
                // Variable pre-mapping (Extracting the "Anchor")
                // ---------------------------------------------------------------------------------
                // In this state, exactly ONE point is known out of the four variables (A, B, C, D).
                // We identify:
                //   1. anchor_point: The index of the geometric point that is already bound.
                //   2. other_seg1_idx: The local variable index for the OTHER half of the anchor's segment.
                //   3. seg2_idx_a / seg2_idx_b: The local variable indices for the entirely free second segment.
                //
                // Example: If 0b1000 (A is known), the anchor segment is AB.
                // Therefore, 'other_seg1_idx' must map to B (local_var_indexes[1]).
                // The free segment is CD, so its variables map to C [2] and D [3].
                // ---------------------------------------------------------------------------------
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
                                // Permutation 1
                                if (check_var_equality(other_seg1_idx, seg2_idx_a, matching_other_end, pair2.first) &&
                                    check_var_equality(other_seg1_idx, seg2_idx_b, matching_other_end, pair2.second) &&
                                    check_var_equality(seg2_idx_a, seg2_idx_b, pair2.first, pair2.second)) {
                                    
                                    next_extension.clear_assignments();
                                    next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end);
                                    next_extension.add_assignment(predicate.variable_indices[seg2_idx_a], pair2.first);
                                    next_extension.add_assignment(predicate.variable_indices[seg2_idx_b], pair2.second);
                                    co_yield next_extension;
                                }
                            
                                // Permutation 2
                                if (check_var_equality(other_seg1_idx, seg2_idx_a, matching_other_end, pair2.second) &&
                                    check_var_equality(other_seg1_idx, seg2_idx_b, matching_other_end, pair2.first) &&
                                    check_var_equality(seg2_idx_a, seg2_idx_b, pair2.second, pair2.first)) {
                                    
                                    next_extension.clear_assignments();
                                    next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end);
                                    next_extension.add_assignment(predicate.variable_indices[seg2_idx_a], pair2.second);
                                    next_extension.add_assignment(predicate.variable_indices[seg2_idx_b], pair2.first);
                                    co_yield next_extension;
                                }
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

                // Variable pre-mapping
                // Extract the anchors and the other ends of the segments. For more clarification, check the case above (for 1 point known).
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

                            // --- Check if the relationship between the two variables is the same as that of between the 2 points ---
                            if (!check_var_equality(other_seg1_idx, other_seg2_idx, matching_other_end_seg_1, matching_other_end_seg_2)) continue;

                            // Safe to assign!
                            next_extension.clear_assignments();

                            // Avoid adding assignment twice if the variable is the same (and maps to the same point)
                            // This prevents us from doing excess memory allocations
                            if (other_seg1_idx == other_seg2_idx) {
                                // These have the same variable index, so they are the same vairable(e.g., cong A B A C). 
                                next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end_seg_1);
                            } else {
                                // The two variables have different indexes (e.g., cong A B C D).
                                next_extension.add_assignment(predicate.variable_indices[other_seg1_idx], matching_other_end_seg_1);
                                next_extension.add_assignment(predicate.variable_indices[other_seg2_idx], matching_other_end_seg_2);
                            }

                            co_yield next_extension;
                        }
                    }
                }
                break;
            }
            
            // Case: 0 Points Known (Brute Force Combinations)
            case 0b0000:
            {
                // Yield every valid matching length pair in the geometry.
                for (const auto &bucket : cache.segment_length_buckets().buckets) {
                    for (size_t i = 0; i < bucket.size(); ++i) {
                        for (size_t j = 0; j < bucket.size(); ++j) {
                            const PointPair &p1 = all_point_pairs[bucket[i]];
                            const PointPair &p2 = all_point_pairs[bucket[j]];

                            if (mapping.is_point_used(p1.first) || mapping.is_point_used(p1.second) ||
                                mapping.is_point_used(p2.first) || mapping.is_point_used(p2.second)) continue;

                            // The 4 combinations (swap_state)
                            // We have two segments: p1(first, second) and p2(first, second).
                            // A segment has no ordering, but it matters for variable assignment.
                            // Mapping A->first, B->second is different to A->second, B->first.
                            //
                            // We use a 0 to 3 loop (binary 00, 01, 10, 11) as a truth table.
                            // - The 1st bit (swap_state & 1) controls if we flip segment p1.
                            // - The 2nd bit (swap_state & 2) controls if we flip segment p2.
                            // 
                            // 0 (00): p1 normal, p2 normal
                            // 1 (01): p1 flipped, p2 normal
                            // 2 (10): p1 normal, p2 flipped
                            // 3 (11): p1 flipped, p2 flipped
                            for (int swap_state = 0; swap_state < 4; ++swap_state) {
                                ProblemPointIndex pt_a = (swap_state & 1) ? p1.second : p1.first;
                                ProblemPointIndex pt_b = (swap_state & 1) ? p1.first : p1.second;
                                ProblemPointIndex pt_c = (swap_state & 2) ? p2.second : p2.first;
                                ProblemPointIndex pt_d = (swap_state & 2) ? p2.first : p2.second;

                                // --- Variable equality check ---
                                // If the variables are the same, then the mapped points have to be the same as well
                                // Otherwise, if the variables are different, then the mapped points have to be different too
                                if (!check_var_equality(local_var_indexes[0], local_var_indexes[1], pt_a, pt_b) ||
                                    !check_var_equality(local_var_indexes[0], local_var_indexes[2], pt_a, pt_c) ||
                                    !check_var_equality(local_var_indexes[0], local_var_indexes[3], pt_a, pt_d) ||
                                    !check_var_equality(local_var_indexes[1], local_var_indexes[2], pt_b, pt_c) ||
                                    !check_var_equality(local_var_indexes[1], local_var_indexes[3], pt_b, pt_d) ||
                                    !check_var_equality(local_var_indexes[2], local_var_indexes[3], pt_c, pt_d)) {
                                    continue;
                                }

                                next_extension.clear_assignments();
                                next_extension.add_assignment(predicate.variable_indices[local_var_indexes[0]], pt_a);
                                next_extension.add_assignment(predicate.variable_indices[local_var_indexes[1]], pt_b);
                                next_extension.add_assignment(predicate.variable_indices[local_var_indexes[2]], pt_c);
                                next_extension.add_assignment(predicate.variable_indices[local_var_indexes[3]], pt_d);
                            
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
        assert(predicate.pattern.args.size() == 4);
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