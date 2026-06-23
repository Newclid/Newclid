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

BOOST_AUTO_TEST_SUITE_END()