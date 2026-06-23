#define BOOST_TEST_MODULE base_provider_test

#include <boost/test/unit_test.hpp>
#include <memory>
#include <vector>
#include <string>
#include <set>

#include "matchers/base_provider.hpp"
#include "problem.hpp"
#include "matchers/lazy_geometry_cache.hpp"
#include "matchers/mapping_state.hpp"
#include "matchers/rule_plan.hpp"
#include "rules/rule_schema.hpp"

using namespace Yuclid;

struct BaseProviderFixture {
    Problem prob;
    BaseProvider base_provider;
};

BOOST_FIXTURE_TEST_SUITE(base_provider_suite, BaseProviderFixture)

BOOST_AUTO_TEST_CASE(base_provider_estimate_math) {
    for(int i=0; i<5; ++i) (void) prob.add_point("P" + std::to_string(i), i, i);
    LazyGeometryCache cache(prob);

    // Test Standard Generator (coll)
    RuleSchema schema_coll;
    schema_coll.id = "test_coll";
    schema_coll.variables = {"A", "B", "C"};
    schema_coll.hypotheses.push_back({"coll", {"A", "B", "C"}});

    RulePlan plan_coll = build_rule_plan(schema_coll);
    BOOST_REQUIRE_EQUAL(plan_coll.candidate_generators.size(), 1);
    
    MappingState mapping_coll(schema_coll, prob);
    
    // We have 3 unique unassigned variables (A, B, C) and 5 free points.
    // BaseProvider math: Permutations P(5, 3) = 5 * 4 * 3 = 60.
    // coll base_cost = 10. Total estimate = 10 + 60 = 70.
    std::size_t est_coll = base_provider.estimate_extensions(plan_coll.candidate_generators[0], mapping_coll, cache);
    BOOST_CHECK_EQUAL(est_coll, 70);
}

BOOST_AUTO_TEST_CASE(base_provider_estimate_penalty_math) {
    for(int i=0; i<5; ++i) (void) prob.add_point("P" + std::to_string(i), i, i);
    LazyGeometryCache cache(prob);

    // Test Unsupported Predicate Penalty
    RuleSchema schema_unsupported;
    schema_unsupported.id = "test_unsupported";
    schema_unsupported.variables = {"A", "B"};
    schema_unsupported.hypotheses.push_back({"fake_rule", {"A", "B"}});

    RulePlan plan_unsupported = build_rule_plan(schema_unsupported);
    BOOST_REQUIRE_EQUAL(plan_unsupported.unsupported_predicates.size(), 1);

    MappingState mapping_unsupported(schema_unsupported, prob);
    
    // P(5, 2) = 20. Unsupported base_cost = 1,000,000. Total = 1,000,020.
    std::size_t est_unsupported = base_provider.estimate_extensions(plan_unsupported.unsupported_predicates[0], mapping_unsupported, cache);
    BOOST_CHECK_EQUAL(est_unsupported, 1'000'020);
}

BOOST_AUTO_TEST_CASE(base_provider_generate_permutations) {
    for(int i=0; i<4; ++i) (void) prob.add_point("P" + std::to_string(i), i, i);
    LazyGeometryCache cache(prob);

    // Create a schema that uses exactly 2 UNIQUE variables to test P(4, 2)
    RuleSchema schema;
    schema.id = "test_perms";
    schema.variables = {"A", "B"};
    schema.hypotheses.push_back({"coll", {"A", "B", "A"}}); // Reuses A, so only 2 unique vars to map

    RulePlan plan = build_rule_plan(schema);
    BOOST_REQUIRE_EQUAL(plan.candidate_generators.size(), 1);

    MappingState mapping(schema, prob);

    // We expect P(4, 2) = 4 * 3 = 12 unique extensions.
    auto generator = base_provider.generate_extensions(plan.candidate_generators[0], mapping, cache);
    
    std::set<std::string> unique_signatures;
    std::size_t count = 0;

    for (const MappingExtension& ext : generator) {
        count++;
        std::string sig = "";
        for (const auto& assignment : ext.assignments()) {
            sig += std::to_string(assignment.variable_idx) + "->" + std::to_string(assignment.point_idx) + "|";
        }
        unique_signatures.insert(sig);
    }

    BOOST_CHECK_EQUAL(count, 12);
    BOOST_CHECK_EQUAL(unique_signatures.size(), 12); 
}

BOOST_AUTO_TEST_CASE(base_provider_generate_too_many_vars_early_exit) {
    // Only 2 points in geometry
    (void) prob.add_point("P1", 0, 0);
    (void) prob.add_point("P2", 1, 1);
    LazyGeometryCache cache(prob);

    RuleSchema schema;
    schema.id = "test_impossible";
    schema.variables = {"A", "B", "C"};
    schema.hypotheses.push_back({"coll", {"A", "B", "C"}});

    RulePlan plan = build_rule_plan(schema);
    MappingState mapping(schema, prob);

    // Predicate wants 3 unique variables, but only 2 free points exist.
    auto generator = base_provider.generate_extensions(plan.candidate_generators[0], mapping, cache);
    
    std::size_t count = 0;
    for (const auto& ext : generator) {
        (void) ext;
        count++;
    }

    // Should yield 0 items
    BOOST_CHECK_EQUAL(count, 0);
}

BOOST_AUTO_TEST_CASE(base_provider_is_satisfied_numerical_check) {
    // 3 perfectly collinear points
    (void) prob.add_point("P1", 0.0, 0.0);
    (void) prob.add_point("P2", 1.0, 0.0);
    (void) prob.add_point("P3", 2.0, 0.0);
    LazyGeometryCache cache(prob);

    RuleSchema schema;
    schema.id = "test_satisfied";
    schema.variables = {"A", "B", "C"};
    schema.hypotheses.push_back({"coll", {"A", "B", "C"}});

    RulePlan plan = build_rule_plan(schema);
    MappingState mapping(schema, prob);

    // Manually assign them in the mapping state to simulate the end of a branch
    bool res1 = mapping.try_apply_assignment(0, 0); // A -> P1
    bool res2 = mapping.try_apply_assignment(1, 1); // B -> P2
    bool res3 = mapping.try_apply_assignment(2, 2); // C -> P3

    BOOST_CHECK(res1 && res2 && res3);

    // The base provider should build the coll statement and check it numerically
    bool satisfied = base_provider.is_satisfied(plan.candidate_generators[0], mapping, cache);
    BOOST_CHECK_EQUAL(satisfied, true);
}

BOOST_AUTO_TEST_SUITE_END()