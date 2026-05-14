#include "matchers/generic_rule_matcher.hpp"

#include "problem.hpp"
#include "rules/rule_schema.hpp"
#include "rules/rule_mapping.hpp"
#include "theorem.hpp"
#include "rules/theorem_builder.hpp"

#include <boost/log/trivial.hpp>
#include <span>

using namespace std;

namespace Yuclid {
    namespace {
        // TODO: A guard is needed to prevent too many nested recursions. 
        // A decision should be made about the stage of the process at which this guard should be implemented.
        //
        // If the guard is not implemented inside this function,
        // be aware that its callers should mind the size of the rule_variables parameter
        void generate_distinct_mappings(
            const std::vector<std::string>& rule_variables, 
            size_t current_var_index, 
            const std::vector<Point> &all_problem_points,
            std::vector<bool> &used_points,
            RuleMapping &current_mapping,
            std::vector<RuleMapping> &valid_results
        ) {
            
            if(current_var_index == rule_variables.size()) {
                valid_results.push_back(current_mapping);
                return;
            }

            const std::string& current_var = rule_variables[current_var_index];

            for(size_t i = 0; i < all_problem_points.size(); ++i){
                if(used_points[i]){
                    continue;
                }

                used_points[i] = true;
                current_mapping.insert_or_assign(current_var, all_problem_points[i]);

                generate_distinct_mappings(rule_variables, current_var_index + 1, all_problem_points, used_points, current_mapping, valid_results);
                
                used_points[i] = false;
            }
        }
    }

    GenericRuleMatcher::GenericRuleMatcher(const Problem *prob, std::span<const RuleSchema> rules) :
    m_problem(prob), m_rules(rules) {
    }

    std::vector<Theorem> GenericRuleMatcher::match() const{
        std::vector<Theorem> generated_theorems;
        for(const RuleSchema &rule_schema: m_rules){
            std::vector<RuleMapping> rule_mappings = find_mappings_for_rule(rule_schema);

            for(const RuleMapping &mapping: rule_mappings){
                Theorem candidate = build_theorem_from_rule_schema(rule_schema, mapping);
                
                // Skip degenerate cases
                if (!candidate.check_hypotheses_nondeg_numerically()) {
                    continue; 
                }

                if(candidate.check_numerically()){
                    // Normalize the theorems in case this method is called from someplace that doesn't do it already
                    // The TheoremMatcher class normalizes them anyways so this is a duplication
                    generated_theorems.push_back(candidate.normalize());
                }
            }
        }
        return generated_theorems;
    }


    std::vector<RuleMapping> GenericRuleMatcher::find_mappings_for_rule(const RuleSchema &schema) const {
        std::vector<RuleMapping> results;
        RuleMapping current_mapping;
        auto all_points_view = m_problem->all_points();
        const std::vector<Point> all_problem_points(all_points_view.begin(), all_points_view.end());
        std::vector<bool> used_points(all_problem_points.size(), false);
    
        generate_distinct_mappings(schema.variables, 0, all_problem_points, used_points, current_mapping, results);
        return results;
    }
}