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
#include "rules/schema_validator.hpp"

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
        add_providers_to_registry();
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
            try {
                // Schema validation
                // Catch typos, bad arity, and missing variables.
                std::optional<std::string> validation_error = validate_schema(schema);
                if (validation_error.has_value()) {
                    BOOST_LOG_TRIVIAL(warning) << validation_error.value();
                    continue; 
                }

                // TODO: decide what to do if we let different varables map to the same point
                if(schema.variables.size() > m_problem->num_points()) {
                    BOOST_LOG_TRIVIAL(warning) << "Generic rule matcher skipped rule " << schema.id << ". Reason: Insufficient number of points in problem.";
                    continue;
                }

                // plan stage
                RulePlan current_plan = build_rule_plan(schema);
                if(current_plan.unsupported_predicates.size() > 0) {
                    BOOST_LOG_TRIVIAL(warning) << "Generic rule matcher skipped rule " 
                                                << schema.id << ". Reason: The schema contains " 
                                                << current_plan.unsupported_predicates.size() << " unsupported predicates.";
                    continue;
                }

                // setup for search stage
                MappingState mapping_state(schema, *m_problem);
                std::vector<RuleMapping> mapping_results;
                FilterState filter_state(current_plan.validators.size());

                // search stage
                search(current_plan, mapping_state, filter_state, geometry_cache, mapping_results);

                // build stage
                std::vector<Theorem> valid_theorems = build_valid_theorems_from_mappings(schema, mapping_results);

                for(auto &candidate : valid_theorems) {
                    all_correct_generated_theorems.push_back(std::move(candidate));
                }
                
            } catch (const std::exception &e) {
                BOOST_LOG_TRIVIAL(warning)
                    << "Skipping custom rule " << schema.id << ": " << e.what();
                continue;
            }
        }

        return all_correct_generated_theorems;
    }
    
    const PlannedPredicate* GenericRuleMatcher::get_cheapest_predicate(
        const std::vector<PlannedPredicate> &predicates,
        const MappingState &state,
        LazyGeometryCache &cache
    ) const {
        const PlannedPredicate* cheapest_predicate = nullptr;
        std::size_t least_extensions = std::numeric_limits<std::size_t>::max();

        for(const PlannedPredicate &candidate: predicates){
            // if everything in the generator is assigned skip it
            // TODO: Decide wether to run is_satisfied? 
            // But then there has to be an indication of wether were evaluating generators or filters (filters are already checked, no need to do it twice)
            // Predicates that already have their own provider will probably not cost to check, but the ones from the base provider will slow things down
            if(are_pattern_variables_assigned(candidate, state)) continue;

            // get provider and metadata
            const PredicateProvider* candidate_provider = m_provider_registry.get_provider(candidate.pattern.name);

            // estimate cost for candidate
            std::size_t expected_extensions = candidate_provider->estimate_extensions(
                candidate,
                state,
                cache
            );

            // choose cheapest
            if(least_extensions > expected_extensions){
                least_extensions = expected_extensions;
                cheapest_predicate = &candidate;
            }
        }

        return cheapest_predicate;
    }

    std::vector<Theorem> GenericRuleMatcher::build_valid_theorems_from_mappings(const RuleSchema &schema, const std::vector<RuleMapping> &mappings) const {
        std::vector<Theorem> theorems;

        for(const RuleMapping &mapping: mappings){
            Theorem candidate = build_theorem_from_rule_schema(schema, mapping);
            if (!candidate.check_hypotheses_nondeg_numerically()) {
                continue;
            }
            if(candidate.check_numerically()){
                theorems.push_back(candidate.normalize());
            }
        }

        return theorems;
    }

    void GenericRuleMatcher::search(
        const RulePlan &plan,
        MappingState &mapping_state,
        FilterState &filter_state,
        LazyGeometryCache &geometry_cache,
        std::vector<RuleMapping> &results
    ) const {
        // Save the state of filters on this level
        FilterStateSnapshot filter_snapshot = filter_state.snapshot();

        // FILTER STAGE
        for(std::size_t i = 0; i < plan.validators.size(); ++i){
            if(filter_state.is_used(i)) continue;

            const PlannedPredicate &candidate_filter = plan.validators[i];

            // Skip filters that require variables not yet assigned in the current mapping state.
            if(!are_pattern_variables_assigned(candidate_filter, mapping_state)) continue;

            const PredicateProvider* candidate_provider = m_provider_registry.get_provider(candidate_filter.pattern.name);

            // If a fully-assigned filter fails, the current partial mapping is invalid.
            // Prune this branch, revert state, and backtrack
            if(!candidate_provider->is_satisfied(candidate_filter, mapping_state, geometry_cache)){
                // Revert any filters that may have passed on this node
                filter_state.rollback(filter_snapshot);
                return;
            }

            // If the filter was satisfied, mark it as used
            filter_state.mark_used(i);
        }

        // BASE CASE
        // If all variables are mapped, this is a valid leaf node. Yield the mapping.
        if(mapping_state.is_complete()) {
            results.push_back(std::move(mapping_state.to_rule_mapping().value()));
            filter_state.rollback(filter_snapshot);
            return;
        }

        // Select the optimal (lowest cost) predicate to generate the next set of assignments.
        const PlannedPredicate* cheapest_predicate = get_cheapest_predicate(plan.candidate_generators, mapping_state, geometry_cache);

        // If no suitable generators were found, choose from the remaining list of filters
        if(cheapest_predicate == nullptr) {
            cheapest_predicate = get_cheapest_predicate(plan.validators, mapping_state, geometry_cache);
        }


        // RECURSIVE STEP
        if(cheapest_predicate != nullptr){
            const PredicateProvider* generator_provider = m_provider_registry.get_provider(cheapest_predicate->pattern.name);

            // Preserve the current variable assignments before descending deeper into the tree
            MappingStateSnapshot variable_snapshot = mapping_state.snapshot();

            // generate_extensions returns a generator
            auto extensions = generator_provider->generate_extensions(*cheapest_predicate, mapping_state, geometry_cache);
            
            // Lazily evaluate and consume the mapping extensions yielded by the coroutine generator
            for(const MappingExtension &extension: extensions){

                // Attempt to apply the generated extension
                if(mapping_state.try_apply_extension(extension)){
                    search(plan, mapping_state, filter_state, geometry_cache, results);     // Recurse (go deeper in the tree)
                    mapping_state.rollback(variable_snapshot);                              // Backtrack
                }
            }
        }
        else {
            throw std::runtime_error(
                "Dead end reached: All predicates evaluated, but the mapping is incomplete. "
                "This indicates unbound variables in the rule schema that are not constrained by any predicate."
            );
        }

        // Reset the filters from this level before returning to the parent
        filter_state.rollback(filter_snapshot);
    }
}