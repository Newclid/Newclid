#include "base_provider.hpp"
#include "statement/statement_builder.hpp"
#include "predicate_matching_metadata.hpp"
#include "statement/statement.hpp"
#include "matchers/mapping_state.hpp"

namespace Yuclid {
     namespace {
        // TODO: Test this extensively!
        // Relies on the sequence from middle to last element being sorted in ascending order
        template<class BidirIt>
        bool next_partial_permutation(BidirIt first, BidirIt middle, BidirIt last) {
            // Reverse the order from middle to last element
            // Since the inital sequence was in ascending order, this puts the elements from 
            // middle to last in descending order
            std::reverse(middle, last);

            // Next_permutation is implemented in a way, where looking from right to left, 
            // it will skip the elements that are in descending order (descending read from left to right)
            // untill it finds the one that isn't (in this case, because we reversed the sequence, that will be the element just before middle).
            // When it finds that element, the method will swap it with the smallest larger element it can find on the right (the descending sequence).
            // Finally the method will reverse the descending sequence and it will put it again in ascending order.
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