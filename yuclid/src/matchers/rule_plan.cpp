#include "matchers/rule_plan.hpp"

#include <algorithm>
#include <iterator>
#include <stdexcept>
#include <utility>

namespace Yuclid {

    namespace {

        bool is_rule_variable(
            const RuleSchema &schema,
            const std::string &arg
        ) {
            return std::ranges::find(schema.variables, arg) != schema.variables.end();
        }

        RuleVariableIndex find_rule_variable_index (
            const RuleSchema &schema,
            const std::string &variable
        ) {
            auto it = std::ranges::find(schema.variables, variable);

            if(it == schema.variables.end()) {
                throw std::runtime_error("Unknown rule variable in predicate: " + variable);
            }

            return static_cast<RuleVariableIndex>(
                std::distance(schema.variables.begin(), it)
            );
        }

        std::vector<RuleVariableIndex> extract_variables(
            const RuleSchema &schema,
            const RulePredicatePattern &pattern
        ) {
            std::vector<RuleVariableIndex> variable_indices;
            variable_indices.reserve(pattern.args.size());

            for(const std::string &arg : pattern.args) {
                if(!is_rule_variable(schema, arg)) {
                    continue;
                }

                RuleVariableIndex variable_index = 
                    find_rule_variable_index(schema, arg);

                if(std::ranges::find(variable_indices, variable_index) == variable_indices.end()) {
                    variable_indices.push_back(variable_index);
                }
            }

            return variable_indices;
        }

        void add_planned_predicate(
            RulePlan &plan,
            const RulePredicatePattern &pattern
        ) {
            const RuleSchema &plan_schema = *plan.schema;

            PlannedPredicate planned {
                .pattern = pattern,
                .metadata = predicate_matching_metadata(pattern.name),
                .variable_indices = extract_variables(plan_schema, pattern),
            };

            switch (planned.metadata.role) {
                case PredicateMatchingRole::CandidateGenerator:
                    plan.candidate_generators.push_back(std::move(planned));
                    break;
                case PredicateMatchingRole::CandidateFilter:
                    plan.candidate_filters.push_back(std::move(planned));
                    break;
                case PredicateMatchingRole::Validator:
                    plan.validators.push_back(std::move(planned));
                    break;
                case PredicateMatchingRole::Unsupported:
                    plan.unsupported_predicates.push_back(std::move(planned));
                    break;
            }
        }

    }

    RulePlan build_rule_plan(
        const RuleSchema &schema
    ) {
        RulePlan plan{};
        plan.schema = &schema;

        for(const RulePredicatePattern &hypothesis : schema.hypotheses) {
            add_planned_predicate(plan, hypothesis);
        }

        for(const RulePredicatePattern &conclusion: schema.conclusions) {
            add_planned_predicate(plan, conclusion);
        }

        return plan;
    }

    std::vector<RulePlan> build_rule_plans(
        const std::vector<RuleSchema> &schemas
    ) {
        std::vector<RulePlan> plans;
        plans.reserve(schemas.size());

        for(const RuleSchema &schema : schemas) {
            plans.push_back(build_rule_plan(schema));
        }

        return plans;
    }

}
