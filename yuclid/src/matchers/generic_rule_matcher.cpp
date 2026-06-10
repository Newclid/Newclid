#include "matchers/generic_rule_matcher.hpp"

#include "problem.hpp"
#include "rules/rule_schema.hpp"
#include "rules/rule_mapping.hpp"
#include "theorem.hpp"
#include "rules/theorem_builder.hpp"
#include "rule_plan.hpp"
#include "predicate_provider.hpp"
#include "base_provider.hpp"
#include "lazy_geometry_cache.hpp"
#include "filter_state.hpp"

#include <boost/log/trivial.hpp>
#include <span>

using namespace std;

namespace Yuclid {
    namespace {
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

        bool are_pattern_variables_assigned(const PlannedPredicate &predicate, const MappingState &state){
            for(RuleVariableIndex idx: predicate.variable_indices){
                if(!state.is_assigned(idx)) return false;
            }
            return true;
        }
    }

    GenericRuleMatcher::GenericRuleMatcher(const Problem *prob, std::span<const RuleSchema> rules) :
    m_problem(prob), m_rules(rules), m_provider_registry(make_unique<BaseProvider>()) {
        add_providers_to_registry();{
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

        if(schema.variables.size() > MAX_VARIABLES_FOR_NAIVE_MATCHING){
            BOOST_LOG_TRIVIAL(warning)  << "Rule " << schema.id << " has too many variables ("
                                        << schema.variables.size() << ") for naive matching. Skipping...";
            return results;
        }

        RuleMapping current_mapping;
        auto all_points_view = m_problem->all_points();
        const std::vector<Point> all_problem_points(all_points_view.begin(), all_points_view.end());
        std::vector<bool> used_points(all_problem_points.size(), false);
    
        generate_distinct_mappings(schema.variables, 0, all_problem_points, used_points, current_mapping, results);
        return results;
    }

    void GenericRuleMatcher::add_providers_to_registry() {
        // add all providers that are implemented
        // m_provider_registry.register_provider(pred_name, provider);
    }

    std::vector<Theorem> GenericRuleMatcher::optimized_match() const {
        std::vector<Theorem> all_correct_generated_theorems;
        LazyGeometryCache geometry_cache(*m_problem);

        for(const RuleSchema &schema: m_rules){
            // plan stage
            RulePlan current_plan = build_rule_plan(schema);
            MappingState mapping_state(schema, *m_problem);
            std::vector<RuleMapping> mapping_results;
            FilterState filter_state(current_plan.candidate_filters.size());

            // search stage
            search(current_plan, mapping_state, filter_state, geometry_cache, mapping_results);

            // build stage
            std::vector<Theorem> valid_theorems = build_valid_theorems_from_mappings(schema, mapping_results);

            for(auto &candidate : valid_theorems) {
                all_correct_generated_theorems.push_back(std::move(candidate));
            }
        }

        return all_correct_generated_theorems;
    }

    const PlannedPredicate* GenericRuleMatcher::get_cheapest_predicate(
        const std::vector<PlannedPredicate> &predicates,
        const MappingState &state,
        LazyGeometryCache &cache
    ) const {}

    std::vector<Theorem> GenericRuleMatcher::build_valid_theorems_from_mappings(const RuleSchema &schema, const std::vector<RuleMapping> &mappings) const {

    }

    void GenericRuleMatcher::search(
        const RulePlan &plan,
        MappingState &mapping_state,
        FilterState &filter_state,
        LazyGeometryCache &geometry_cache,
        std::vector<RuleMapping> &results
    ) const {
    }
}