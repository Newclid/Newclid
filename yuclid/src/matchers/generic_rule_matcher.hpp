#pragma once

#include "problem.hpp"
#include "rules/rule_schema.hpp"
#include "rules/rule_mapping.hpp"
#include "theorem.hpp"
#include "predicate_provider.hpp"
#include "filter_state.hpp"

#include <span>

namespace Yuclid {
    class GenericRuleMatcher {
        public:
            GenericRuleMatcher(const Problem *prob, std::span<const RuleSchema> rules);

            [[nodiscard]] std::vector<Theorem> match() const;
            [[nodiscard]] std::vector<Theorem> optimized_match() const;

        private:
            const Problem *m_problem;
            std::span<const RuleSchema> m_rules;
            PredicateProviderRegistry m_provider_registry;

            //Safety limit for naive matching
            static constexpr size_t MAX_VARIABLES_FOR_NAIVE_MATCHING = 6;
            [[nodiscard]] std::vector<RuleMapping> find_mappings_for_rule(const RuleSchema &schema) const;
            [[nodiscard]] std::vector<Theorem> build_valid_theorems_from_mappings(const RuleSchema &schema, const std::vector<RuleMapping> &mappings) const;
            void add_providers_to_registry();
            void search(
                const RulePlan &plan,
                MappingState &current_state,
                FilterState &filter_state,
                LazyGeometryCache &geometry_cache,
                std::vector<RuleMapping> &results
            ) const;
            const PlannedPredicate* get_cheapest_predicate(const std::vector<PlannedPredicate> &predicates, const MappingState &state, LazyGeometryCache &cache) const;
    };
}