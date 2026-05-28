#pragma once

#include "problem.hpp"
#include "rules/rule_schema.hpp"
#include "rules/rule_mapping.hpp"
#include "theorem.hpp"

#include <span>

namespace Yuclid {
    class GenericRuleMatcher {
        public:
            GenericRuleMatcher(const Problem *prob, std::span<const RuleSchema> rules);

            [[nodiscard]] std::vector<Theorem> match() const;

        private:
            const Problem *m_problem;
            std::span<const RuleSchema> m_rules;

            [[nodiscard]] std::vector<RuleMapping> find_mappings_for_rule(const RuleSchema &schema) const;
            //Safety limit for naive matching
            static constexpr size_t MAX_VARIABLES_FOR_NAIVE_MATCHING = 6;
    };
}