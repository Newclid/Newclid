#pragma once

#include <vector>
#include "matchers/matching_types.hpp"
#include "matchers/predicate_matching_metadata.hpp"
#include "rules/rule_schema.hpp"

namespace Yuclid {

struct PlannedPredicate {
    RulePredicatePattern pattern;
    PredicateMatchingMetadata metadata;
    std::vector<RuleVariableIndex> variable_indices;
};

/**
 * Matching-oriented plan derived from a RuleSchema.
 *
 * The RuleSchema remains the source of truth for the rule id, variables,
 * original hypotheses, and conclusions. RulePlan only stores the derived
 * information needed by the optimized matcher.
 *
 * The schema pointer must outlive this RulePlan.
 */
struct RulePlan {
    const RuleSchema *schema;
    std::vector<PlannedPredicate> candidate_generators;
    std::vector<PlannedPredicate> candidate_filters;
    std::vector<PlannedPredicate> validators;
    std::vector<PlannedPredicate> unsupported_predicates;
};

[[nodiscard]] RulePlan build_rule_plan(
    const RuleSchema &schema
);

[[nodiscard]] std::vector<RulePlan> build_rule_plans(
    const std::vector<RuleSchema> &schemas
);

}
