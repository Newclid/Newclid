#include "predicate_provider.hpp"
#include "mapping_state.hpp"
#include "lazy_geometry_cache.hpp"     
#include "rule_plan.hpp"
#include "geometry_cache_types.hpp"
#include "numbers/util.hpp"

#include <unordered_map>
#include <cassert>

namespace Yuclid {
    namespace {
        std::array<RuleVariableIndex, 4> get_predicate_local_var_indexes(const PlannedPredicate &predicate) {
            std::array<RuleVariableIndex, 4> predicate_var_indexes;
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
            std::array<RuleVariableIndex, 4> local_predicate_indexes = get_predicate_local_var_indexes(predicate);

            for(int i = 0; i < 4; i++){
                assert(local_predicate_indexes[i] < predicate.variable_indices.size() 
                && "Cong provider ran into an issue, predicate-local varaible indexes indicate more unique variables than the planned predicate has.");

                // Get the optional point index for each variable. Map predicate-local variable indexes to the indexes of the variables in the schema.
                assignments[i] = mapping.assigned_point_index(predicate.variable_indices[local_predicate_indexes[i]]);
            }
            
            return assignments;
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

        // Generate the bitmask (A = bit 3, B = bit 2, C = bit 1, D = bit 0)
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
        bool intrsect_estimates_with_point = false;

        switch (state_mask) {
            case 0b1111:
                // All 4 points assigned. No extensions to generate.
                estimate = 0;
                break;

            case 0b1110: // AB and C assigned, D free
            case 0b1101: // AB and D assigned, C free
            case 0b1011: // B free, A and CD assigned
            case 0b0111: // A free, B and CD assigned
                intrsect_estimates_with_point = true;
                [[fallthrough]];
            case 0b1100: // AB assigned, CD free
            case 0b0011: // AB free, CD assigned
                // The length is known! 
                double assigned_length = 0;
                if((state_mask & 0b1100) == 0b1100) {
                    assigned_length = static_cast<double>(SquaredDist(cache.point(*assignments[0]), cache.point(*assignments[1])));
                }
                else {
                    assigned_length = static_cast<double>(SquaredDist(cache.point(*assignments[2]), cache.point(*assignments[3]))); 
                }
                
                const auto &all_point_pairs = cache.point_pairs();

                for (const auto &bucket : cache.segment_length_buckets().buckets) {
                    // buckets are guaranteed to contain at least 2 elements
                    double min_len = static_cast<double>(SquaredDist(cache.point(all_point_pairs[bucket.front()].first), cache.point(all_point_pairs[bucket.front()].second)));
                    double max_len = static_cast<double>(SquaredDist(cache.point(all_point_pairs[bucket.back()].first), cache.point(all_point_pairs[bucket.back()].second)));
                    
                    if (assigned_length >= (min_len - EPS) && assigned_length <= (max_len + EPS)) {
                        // Extract one to exclude the already assigned segment
                        // Multiply by 2 because a segment XY can be mapped as XY or YX!
                        estimate = (bucket.size() - 1) * 2; 
                        break;
                    }
                }
                if(intrsect_estimates_with_point) {
                    estimate = estimate / cache.num_points();
                    estimate = estimate > 0 ? estimate : 1;
                }
                break;
            
            case 0b1010: case 0b1001: case 0b0110: case 0b0101:
                // Two points are known, but length is unknown.
                intrsect_estimates_with_point = true;
                [[fallthrough]];
            case 0b1000: case 0b0100: case 0b0010: case 0b0001:
                // One point is known.
                // Assuming all segments that contain the point are in different buckets, than it appears in at most cache.num_points() - 1 buckets
                // The estimated extensions are therefore, the number of buckets multiplied by the average length of a bucket 
                // Multiplied by 2 becase a segment can be mapped bidirectionally
                estimate = (cache.num_points() - 1) * avg_bucket_size * 2;

                if(intrsect_estimates_with_point) {
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
        // Generate the bitmask (A = bit 3, B = bit 2, C = bit 1, D = bit 0)
        uint8_t state_mask = 0;
        if (assignments[0].has_value()) state_mask |= 0b1000; // Variable A
        if (assignments[1].has_value()) state_mask |= 0b0100; // Variable B
        if (assignments[2].has_value()) state_mask |= 0b0010; // Variable C
        if (assignments[3].has_value()) state_mask |= 0b0001; // Variable D

        switch (state_mask) {
            case 0b1111:
                // All 4 points assigned. No extensions to generate.
                return 0;

            case 0b1100: // AB assigned, CD free
            case 0b0011: // AB free, CD assigned
                // The length is known! 
                // 1. Calculate the distance of the known segment.
                // 2. Find the specific bucket matching that distance.
                // 3. Yield the remaining pairs from that single bucket.
                break;
        
            case 0b1000: // A assigned
            case 0b0100: // B assigned
            case 0b0010: // C assigned
            case 0b0001: // D assigned
                // O(N) FILTER PATH: One point is known.
                // Loop all buckets, but only yield pairs where one segment contains the known point.
                break;
        
            case 0b1010: // A and C assigned
            case 0b1001: // A and D assigned
            case 0b0110: // B and C assigned
            case 0b0101: // B and D assigned
                // Two points known, but length is UNKNOWN.
                // Loop all buckets, find pairs where segment 1 has the first point, 
                // and segment 2 has the second point.
                break;
        
            case 0b0000:
                // Nothing is assigned.
                // Loop all buckets, yield all pair combinations.
                break;
        
            default:
                // Handles states with 3 points assigned (e.g., 0b1110)
                // You know the length (from the 2 connected points), so find that bucket
                // and strictly filter it for the 3rd known point.
                break;
        }
    }

    bool CongProvider::is_satisfied(
        const PlannedPredicate &predicate,
        const MappingState &mapping,
        const LazyGeometryCache &cache
    ) const {
        
    }

}