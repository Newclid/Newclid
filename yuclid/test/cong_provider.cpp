#define BOOST_TEST_MODULE cong_provider_test

#include <boost/test/unit_test.hpp>
#include <memory>
#include <vector>
#include <string>
#include <algorithm>

#include "matchers/cong_provider.hpp"
#include "problem.hpp"
#include "matchers/lazy_geometry_cache.hpp"
#include "matchers/mapping_state.hpp"
#include "matchers/rule_plan.hpp"
#include "rules/rule_schema.hpp"
#include "matchers/predicate_matching_metadata.hpp"

using namespace Yuclid;

struct CongProviderFixture {
    Problem prob;
    RuleSchema schema;
    CongProvider provider;

    CongProviderFixture() {
        schema.id = "test_cong";
        schema.variables = {"A", "B", "C", "D"}; // 4 unique variables
    }

    // Helper to build a planned predicate
    PlannedPredicate build_planned_pred(const std::vector<std::string>& args) {
        PlannedPredicate pp;
        pp.pattern = {"cong", args};
        pp.metadata = predicate_matching_metadata("cong"); // Should get base_cost = 20
        
        for (const auto &arg : args) {
            for (std::size_t i = 0; i < schema.variables.size(); ++i) {
                if (schema.variables[i] == arg && std::find(pp.variable_indices.begin(), pp.variable_indices.end(), i) == pp.variable_indices.end()) {
                    pp.variable_indices.push_back(i);
                    break;
                }
            }
        }
        return pp;
    }

    // Helper to set up a geometric grid
    // 4 points forming a 1x1 square.
    // Length 1.0 segments: 4 (sides)
    // Length sqrt(2) segments: 2 (diagonals)
    // The other buckets are singletons
    void setup_geometry() {
        (void) prob.add_point("P0", 0.0, 0.0); // Index 0
        (void) prob.add_point("P1", 1.0, 0.0); // Index 1
        (void) prob.add_point("P2", 1.0, 1.0); // Index 2
        (void) prob.add_point("P3", 0.0, 1.0); // Index 3
        (void) prob.add_point("P4", 0.0, 5.0); // Index 4
    }
};

BOOST_FIXTURE_TEST_SUITE(cong_provider_phase1_suite, CongProviderFixture)


BOOST_AUTO_TEST_CASE(is_satisfied_numerical_match) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A->P0, B->P1 (Length 1)
    // Map C->P3, D->P2 (Length 1)
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); 
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 3));
    BOOST_REQUIRE(mapping.try_apply_assignment(3, 2));

    BOOST_CHECK_EQUAL(provider.is_satisfied(pp, mapping, cache), true);
}

BOOST_AUTO_TEST_CASE(is_satisfied_numerical_mismatch) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A->P0, B->P1 (Length 1)
    // Map C->P3, D->P4 (Length 4)
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); 
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 3));
    BOOST_REQUIRE(mapping.try_apply_assignment(3, 4));

    BOOST_CHECK_EQUAL(provider.is_satisfied(pp, mapping, cache), false);
}

BOOST_AUTO_TEST_SUITE_END()