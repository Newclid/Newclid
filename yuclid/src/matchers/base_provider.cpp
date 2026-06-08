#include "base_provider.hpp"
#include "statement/statement_builder.hpp"
#include "predicate_matching_metadata.hpp"
#include "statement/statement.hpp"
#include "matchers/mapping_state.hpp"

namespace Yuclid {
     namespace {
        // Generates the next partial permutation of a sequence.
        // PRECONDITION: The tail range [middle, last) MUST be sorted in ascending order.
        template<class BidirIt>
        bool next_partial_permutation(BidirIt first, BidirIt middle, BidirIt last) {
            
            // STEP 1: Reverse the tail.
            // This turns our ascending tail into a strictly descending tail.
            // Example: [ 1 2 | 3 4 5 ] becomes [ 1 2 | 5 4 3 ]
            std::reverse(middle, last);

            // STEP 2: Let std::next_permutation give the next perumtation.
            // next_permutation scans right-to-left to find the first element smaller 
            // than the one to its right (the "pivot"). 
            // Because we made the tail descending, the scan skips the entire tail 
            // and is forced to pick the element immediately before `middle` as the pivot.
            // It swaps that pivot with the smallest element larger than the pivot it can find in the tail.
            // Finally, it automatically reverses the tail back to ascending order.
            // This guarantees that we'll get all partial permutations
            //
            // An example run over a vector {1, 2, 3, 4, 5}, where we generate 
            // partial permutations on the first 2 positions:
            // [ 1 2 | 3 4 5 ]
            // [ 1 3 | 2 4 5 ]
            // [ 1 4 | 2 3 5 ]
            // [ 1 5 | 2 3 4 ]
            // [ 2 1 | 3 4 5 ]
            // [ 2 3 | 1 4 5 ]
            // [ 2 4 | 1 3 5 ]
            // [ 2 5 | 1 3 4 ]
            // [ 3 1 | 2 4 5 ]
            // [ 3 2 | 1 4 5 ]
            // [ 3 4 | 1 2 5 ]
            // [ 3 5 | 1 2 4 ]
            // [ 4 1 | 2 3 5 ]
            // [ 4 2 | 1 3 5 ]
            // [ 4 3 | 1 2 5 ]
            // [ 4 5 | 1 2 3 ]
            // [ 5 1 | 2 3 4 ]
            // [ 5 2 | 1 3 4 ]
            // [ 5 3 | 1 2 4 ]
            // [ 5 4 | 1 2 3 ]
            return std::next_permutation(first, last);
        }

        MappingExtension get_extension_from_permutation(
            const std::vector<RuleVariableIndex> &var_indexes, 
            const std::vector<std::size_t> &point_indexes,
            MappingExtension &result
        ) {
            // TODO: implement this method for mapping extension to avoid allocating/deallocating memory every time
            // result.clear_assignments();
            for(std::size_t i = 0; i < var_indexes.size(); ++i) {
                result.add_assignment(var_indexes[i], point_indexes[i]);
            }
            return result;
        }

        std::size_t variation_with_cap(std::size_t size_of_set, std::size_t num_total_elements) {
            if (size_of_set > num_total_elements) return 0;

            constexpr std::size_t MAX_ESTIMATE_CAP = 100'000'000;
            std::size_t result = 1;
            std::size_t next_element;

            for (std::size_t i = 0; i < size_of_set; ++i) {
                next_element = num_total_elements - i;
                
                if (result > MAX_ESTIMATE_CAP / next_element) {
                    return MAX_ESTIMATE_CAP;
                }

                result *= next_element;
            }
            return result;
        }
    }


    std::size_t BaseProvider::estimate_extensions(
        [[maybe_unused]] const RulePredicatePattern &pattern,
        [[maybe_unused]] const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache,
        [[maybe_unused]] const PredicateMatchingMetadata &predicate_metadata
    ) const {
        std::size_t num_unassigned_vars = mapping.unassigned_variables().size();
        // TODO: get the total number of points, once the cache is actually implemented, remove the placeholder
        std::size_t num_free_points = 0; // = cache.get_problem()->num_points() - unassigned_vars;
        std::size_t estimate = predicate_metadata.base_cost + variation_with_cap(num_unassigned_vars, num_free_points);

        return estimate;
    }

    std::generator<MappingExtension> BaseProvider::generate_extensions(
        [[maybe_unused]] const RulePredicatePattern &pattern,
        const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache
    ) const {
        // TODO: get the total number of points, once the cache is actually implemented
        std::size_t num_points = 0; // = cache.get_problem()->num_points();
        std::vector<RuleVariableIndex> unassigned_vars = mapping.unassigned_variables();
        std::vector<std::size_t> free_points;

        for(std::size_t i = 0; i < num_points; ++i){
            if(!mapping.is_point_used(i)){
                // Points are uniquely represented by their indexes the list of all points in the problem object
                free_points.push_back(i);
            }
        }

        if(unassigned_vars.size() > free_points.size()) {
            throw std::runtime_error("The custom theorem requires more unique points than the problem contains.");
        }

        // This will point past the last position we need for the variation of points
        // This means that if we need 3 points assigned, this will point to the forth one in the vector 
        // it could potentially point to .end() but the check above ensures it will not go past
        std::vector<std::size_t>::iterator nth_position = free_points.begin() + unassigned_vars.size();
        MappingExtension next_extension;

        do {
            next_extension = get_extension_from_permutation(unassigned_vars, free_points, next_extension);
            co_yield next_extension;
        } while(next_partial_permutation(free_points.begin(), nth_position, free_points.end()));
    }

    // TODO: Ensure this is not called on unsupported predicates (ones that will break the statement_builder)
    bool BaseProvider::is_satisfied(
        const RulePredicatePattern &pattern,
        const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache
    ) const {
        // Cast partial mapping to rule mapping
        auto optional_rule_mapping = mapping.to_partial_rule_mapping();

        if (!optional_rule_mapping.has_value()) {
            return false;
        }

        // Build statement from pattern and mapping
        auto statements = build_statements_from_pattern(pattern, optional_rule_mapping.value());
        
        for(const auto &statement : statements) {
            if(!statement->check_numerically()){
                return false;
            }
        }

        return true;
    }
}