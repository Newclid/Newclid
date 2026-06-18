#pragma once

#include "predicate_provider.hpp"
#include "mapping_state.hpp"
#include "lazy_geometry_cache.hpp"         

namespace Yuclid {

    /** * @brief This class implements the congruence provider.
     * Handles matching for the geometric 'cong' predicate (e.g., `cong A B C D`), 
     * which asserts that the segment defined by A and B has the same length as 
     * the segment defined by C and D.
     */
    class CongProvider : public PredicateProvider {
    public:
        /**
         * @brief Calculates a fast, heuristic estimate of how many valid mappings exist for the current state.
         * Utilizes a 4-bit state mask to determine which of the 4 target points are already bound.
         * - If a segment is fully bound (e.g., AB), this returns an exact count by looking up 
         * the corresponding segment length bucket in the geometry cache.
         * - If the length is unknown, it calculates an heuristic approximation based on average 
         * bucket sizes and the number of total points, intentionally avoiding expensive O(N) loops.
         * @param predicate The planned predicate containing the string arguments and schema indices.
         * @param mapping The current search state containing previously bound point assignments.
         * @param cache The lazy geometry cache holding pre-sorted segment length buckets.
         * @return std::size_t The estimated number of valid extensions, plus the metadata base cost.
         */
        [[nodiscard]] std::size_t estimate_extensions(
            const PlannedPredicate &predicate,
            const MappingState &mapping,
            const LazyGeometryCache &cache
        ) const override;

        /**
         * @brief Generates all valid point assignments to satisfy the congruence constraint.
         * - If a segment is known, it directly accesses the specific length bucket 
         * and yields the remaining free pairs.
         * - If independent points are known, it loops the buckets to find segments 
         * that explicitly touch the bound anchor points.
         * - If no points are known, it yields all valid pair combinations from 
         * within the cached length buckets.
         * @param predicate The planned predicate containing the target constraint.
         * @param mapping The current search state.
         * @param cache The lazy geometry cache.
         * @return std::generator<MappingExtension> A lazy generator yielding fully populated extensions.
         */
        [[nodiscard]] std::generator<MappingExtension> generate_extensions(
            const PlannedPredicate &predicate,
            const MappingState &mapping,
            const LazyGeometryCache &cache
        ) const override;

        /**
         * @brief Verifies if a fully bound state mathematically satisfies the congruence constraint.
         * Builds a DistEqDist object (the representation for congruence inside the engine) 
         * and calls its check_nondegen() and check_equations() methods.
         * @param predicate The planned predicate.
         * @param mapping The mapping state containing 4 assigned points.
         * @param cache The lazy geometry cache.
         * @return true If the two segments are congruent within the engine's tolerance parameters.
         * @return false If the segments have different lengths.
         */
        [[nodiscard]] bool is_satisfied(
            const PlannedPredicate &predicate,
            const MappingState &mapping,
            const LazyGeometryCache &cache
        ) const override;
    };

}