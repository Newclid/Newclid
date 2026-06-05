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
    }


    std::size_t BaseProvider::estimate_extensions(
        [[maybe_unused]] const RulePredicatePattern &pattern,
        [[maybe_unused]] const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache,
        [[maybe_unused]] const PredicateMatchingMetadata predicate_metadata
    ) const {
        return std::numeric_limits<std::size_t>::max();
    }

    std::generator<MappingExtension> BaseProvider::generate_extensions(
        const RulePredicatePattern &pattern,
        const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache,
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


        while(std::next_partial_permutation(free_points.begin(), nth_position, free_points.end())){
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