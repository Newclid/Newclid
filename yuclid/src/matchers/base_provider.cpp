#include "base_provider.hpp"
#include "statement/statement_builder.hpp"
#include "predicate_matching_metadata.hpp"
#include "statement/statement.hpp"

namespace Yuclid {
    std::size_t BaseProvider::estimate_extensions(
        [[maybe_unused]] const RulePredicatePattern &pattern,
        [[maybe_unused]] const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache,
        [[maybe_unused]] PredicateMatchingMetadata predicate_metadata
    ) const {
        return std::numeric_limits<std::size_t>::max();
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