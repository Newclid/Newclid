#include "base_provider.hpp"
#include "statement/statement_builder.hpp"
#include "predicate_matching_metadata.hpp"
#include "statement/statement.hpp"
#include "matchers/mapping_state.hpp"

namespace Yuclid {
     namespace {
        template<class BidirIt>
        bool next_partial_permutation(BidirIt first, BidirIt middle, BidirIt last) {
            std::reverse(middle, last);
            return std::next_permutation(first, last);
        }

        MappingExtension get_extension_from_permutation(
            const std::vector<RuleVariableIndex> &var_indexes, 
            const std::vector<std::size_t> &point_indexes
        ) {
            MappingExtension extension;
            for(std::size_t i = 0; i < var_indexes.size(); ++i) {
                extension.add_assignment(var_indexes[i], point_indexes[i]);
            }
            return extension;
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
        // TODO get the total number of points, once the cache is actually implemented
        std::size_t num_unassigned_vars = mapping.unassigned_variables().size();
        std::size_t num_free_points; // = cache.get_problem()->num_points() - unassigned_vars;
        std::size_t estimate = predicate_metadata.base_cost + variation_with_cap(num_unassigned_vars, num_free_points);

        return estimate;
    }

    std::generator<MappingExtension> BaseProvider::generate_extensions(
        [[maybe_unused]] const RulePredicatePattern &pattern,
        const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache
    ) const {
        // TODO get the total number of points, once the cache is actually implemented
        std::size_t num_points; // = cache.get_problem()->num_points();
        std::vector<RuleVariableIndex> unassigned_vars = mapping.unassigned_variables();
        std::vector<std::size_t> free_points;

        for(std::size_t i = 0; i < num_points; ++i){
            if(!mapping.is_point_used(i)){
                free_points.push_back(i);
            }
        }

        if(unassigned_vars.size() > free_points.size()) {
            throw std::runtime_error("The custom theorem requires more unique points than the problem contains.");
        }

        std::vector<std::size_t>::iterator nth_position = free_points.begin() + unassigned_vars.size();


        while(next_partial_permutation(free_points.begin(), nth_position, free_points.end())){
            MappingExtension next_extension = get_extension_from_permutation(unassigned_vars, free_points);
            co_yield next_extension;
        }
    }

    bool BaseProvider::is_satisfied(
        const RulePredicatePattern &pattern,
        const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache
    ) const {
        auto optional_rule_mapping = mapping.to_partial_rule_mapping();

        if (!optional_rule_mapping.has_value()) {
            return false;
        }

        auto statements = build_statements_from_pattern(pattern, optional_rule_mapping.value());
        
        for(const auto &statement : statements) {
            if(!statement->check_numerically()){
                return false;
            }
        }

        return true;
    }
}