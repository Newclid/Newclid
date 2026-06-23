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
        (void) prob.add_point("P0", 0.0, 0.0); // 0
        (void) prob.add_point("P1", 1.0, 0.0); // 1
        (void) prob.add_point("P2", 1.0, 1.0); // 2
        (void) prob.add_point("P3", 0.0, 1.0); // 3
        (void) prob.add_point("P4", 0.0, 5.0); // 4 Outlier
    }
};

BOOST_FIXTURE_TEST_SUITE(cong_provider_phase1_suite, CongProviderFixture)

// Test is_satisfied

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

BOOST_AUTO_TEST_CASE(is_satisfied_failsafe_partial_mapping) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map only 3 variables
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); 
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 3));

    // Should hit the failsafe and return false instead of crashing on empty assignment
    BOOST_CHECK_EQUAL(provider.is_satisfied(pp, mapping, cache), false);
}

BOOST_AUTO_TEST_CASE(is_satisfied_degenerate_segment) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "C"});

    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); // A -> P0
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1)); // B -> P1
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 2)); // C -> P2

    // Congruence requires non-degenerate lines. Check_nondegen() should catch C=C (length 0).
    BOOST_CHECK_EQUAL(provider.is_satisfied(pp, mapping, cache), false);
}

// Test estimate_extensions

BOOST_AUTO_TEST_CASE(estimate_state_1111_all_known) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); 
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 2));
    BOOST_REQUIRE(mapping.try_apply_assignment(3, 3));

    // Estimate should be exactly base_cost (20) + 0 extensions
    BOOST_CHECK_EQUAL(provider.estimate_extensions(pp, mapping, cache), 20);
}

BOOST_AUTO_TEST_CASE(estimate_state_1100_length_known) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); // A -> P0
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1)); // B -> P1

    // The length 1.0 bucket contains 4 segments.
    // P4 (Outlier) doesn't create any length 1.0 segments, so it doesn't affect this bucket.
    // Known segment is excluded (-1) = 3 segments.
    // Directional permutations (*2) = 6 estimates.
    // Total = base_cost (20) + 6 = 26.
    BOOST_CHECK_EQUAL(provider.estimate_extensions(pp, mapping, cache), 26);
}

BOOST_AUTO_TEST_CASE(estimate_state_0000_brute_force) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // 0 points known.
    // 5 points total -> 10 PointPairs.
    // Bucket 1 (Length 1.0) has 4 pairs.
    // Bucket 2 (Length sqrt(2)) has 2 pairs.
    // All distances to P4 are unique, so they are singletons and skipped by the cache builder.
    // avg_bucket_size = total_pairs (10) / num_buckets (2) = 5.
    // Math: num_buckets(2) * (avg_bucket_size(5) * avg_bucket_size(5) * 4) = 2 * (25 * 4) = 200.
    // Total = base_cost (20) + 200 = 220.
    
    std::size_t est = provider.estimate_extensions(pp, mapping, cache);
    BOOST_CHECK_EQUAL(est, 220);
}

BOOST_AUTO_TEST_CASE(estimate_intersection_reduction_applied) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Assign A, B, and C (State 0b1110)
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); 
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 2));

    // Length 1.0 bucket has 4 segments.
    // Base math: (4 - 1) * 2 = 6.
    // N = 5 points in cache.
    // Intersection reduction ceiling division: (6 + N(5) - 1) / 5 = 10 / 5 = 2.
    // Total = base_cost (20) + 2 = 22.
    BOOST_CHECK_EQUAL(provider.estimate_extensions(pp, mapping, cache), 22);
}

BOOST_AUTO_TEST_SUITE_END()