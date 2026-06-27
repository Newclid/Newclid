#define BOOST_TEST_MODULE cong_provider_test

#include <boost/test/unit_test.hpp>
#include <memory>
#include <vector>
#include <string>
#include <set>
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

    // Helper to consume a generator and return unique assignment signatures
    std::set<std::string> consume_generator(std::generator<MappingExtension>& gen) {
        std::set<std::string> unique_signatures;
        for (const MappingExtension& ext : gen) {
            std::string sig = "";
            for (const auto& assignment : ext.assignments()) {
                sig += std::to_string(assignment.variable_idx) + "->" + std::to_string(assignment.point_idx) + "|";
            }
            unique_signatures.insert(sig);
        }
        return unique_signatures;
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
        (void) prob.add_point("P4", 0.0, 5.0); // 4
    }

    // 3x3 Grid (9 points). 
    // Highly connected, lots of segments of length 1, sqrt(2), 2, etc.
    void setup_large_grid() {
        int idx = 0;
        for (int x = 0; x < 3; ++x) {
            for (int y = 0; y < 3; ++y) {
                (void) prob.add_point("G" + std::to_string(idx++), x * 1.0, y * 1.0);
            }
        }
    }

    // Random problems setup, the cache will be empty so estimates should be low too
    void setup_irregular_geometry() {
        (void) prob.add_point("R0", 0.0, 0.0);
        (void) prob.add_point("R1", 1.23, 4.56);
        (void) prob.add_point("R2", -3.14, 2.71);
        (void) prob.add_point("R3", 5.55, -1.11);
        (void) prob.add_point("R4", 0.89, 8.90);
    }

    void setup_very_large_grid() {
        int idx = 0;
        for (int x = 0; x < 5; ++x) {
            for (int y = 0; y < 5; ++y) {
                (void) prob.add_point("M" + std::to_string(idx++), x * 1.0, y * 1.0);
            }
        }
    }

    void run_comparison(CongProvider& cong_provider, PlannedPredicate& pp, MappingState& mapping, LazyGeometryCache& cache, const std::string& name) {
        std::size_t estimate = cong_provider.estimate_extensions(pp, mapping, cache);
        
        auto generator = cong_provider.generate_extensions(pp, mapping, cache);
        std::size_t generated = 0;
        for (const auto& ext : generator) {
            (void) ext;
            generated++;
        }

        BOOST_TEST_MESSAGE("---- " << name << " ----");
        BOOST_TEST_MESSAGE("Estimated Cost: " << estimate);
        BOOST_TEST_MESSAGE("Actually Generated: " << generated);
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

// ----------------------------------------------------------------------
// Generate Extensions Tests
// ----------------------------------------------------------------------

// Fast paths

BOOST_AUTO_TEST_CASE(generation_tautology_0b0000) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    
    // Identity mapping: cong A B A B
    PlannedPredicate pp = build_planned_pred({"A", "B", "A", "B"});

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // 5 points total. We choose 2 distinct points: P(5, 2) = 20 combinations.
    // The fast path should just generate all 20 without looking at lengths.
    BOOST_CHECK_EQUAL(results.size(), 20);
}

BOOST_AUTO_TEST_CASE(generation_tautology_0b1010) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "A", "B"});

    // Map A -> P0
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // A is P0. B can be any of the 4 remaining free points.
    BOOST_CHECK_EQUAL(results.size(), 4);
}

// Test specific bitmasks

BOOST_AUTO_TEST_CASE(generation_state_1111_all_known) {
    setup_geometry();
    LazyGeometryCache cache(prob); 
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 2));
    BOOST_REQUIRE(mapping.try_apply_assignment(3, 3));

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // Nothing left to map, should co_return immediately
    BOOST_CHECK_EQUAL(results.size(), 0);
}

BOOST_AUTO_TEST_CASE(generation_state_1100_segment_known) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // A->P0, B->P1 (Length 1)
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // The length 1 bucket has pairs: (0,1), (1,2), (2,3), (3,0).
    // Points 0 and 1 are used. The only pair using free points is (2,3).
    // We expect 2 permutations: C->2, D->3 AND C->3, D->2.
    BOOST_CHECK_EQUAL(results.size(), 2);
}

BOOST_AUTO_TEST_CASE(generation_state_1110_one_missing) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // A->P0, B->P1 (Length 1)
    // C->P3 (Target anchor)
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 3));

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // D must map to P2 (the only point exactly length 1 away from P3 that isn't P0).
    BOOST_CHECK_EQUAL(results.size(), 1);
}

BOOST_AUTO_TEST_CASE(generation_state_1010_shared_variable) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    
    // Isosceles triangle rule: cong A B A C
    PlannedPredicate pp = build_planned_pred({"A", "B", "A", "C"});

    // Map A -> P0
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // We need segments originating from P0 of equal length.
    // Length 1: (0,1) and (0,3). Thus B=1, C=3 OR B=3, C=1.
    // Length sqrt(2): Only (0,2). We can't have B=2 and C=2 because B and C must be distinct.
    // P4 (Outlier) has no equal length segment.
    BOOST_CHECK_EQUAL(results.size(), 2); 
}

BOOST_AUTO_TEST_CASE(generation_state_0000_brute_force) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    auto generator = provider.generate_extensions(pp, mapping, cache);
    auto results = consume_generator(generator);

    // Bucket 1 (Length 1): (0,1), (1,2), (2,3), (3,0). 
    // Disjoint pairs: [(0,1),(2,3)], [(1,2),(3,0)]. Each gives 8 permutations. = 16 total.
    // Bucket 2 (Length sqrt 2): (0,2), (1,3).
    // Disjoint pairs: [(0,2),(1,3)]. Gives 8 permutations.
    // Total mathematically valid distinct pairs = 24.
    BOOST_CHECK_EQUAL(results.size(), 24);
}

// Compare estimations to generations

// Small benchmarks with (5 Points)

BOOST_AUTO_TEST_CASE(benchmark_small_0000_brute_force) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    run_comparison(provider, pp, mapping, cache, "Small Grid: 0b0000 (Brute Force)");
}

BOOST_AUTO_TEST_CASE(benchmark_small_1000_one_point) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); // A -> P0
    run_comparison(provider, pp, mapping, cache, "Small Grid: 0b1000 (One Point Known)");
}

BOOST_AUTO_TEST_CASE(benchmark_small_1010_two_independent_points) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A -> P0, C -> P2
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); 
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 2));
    run_comparison(provider, pp, mapping, cache, "Small Grid: 0b1010 (Two Independent Points)");
}

BOOST_AUTO_TEST_CASE(benchmark_small_1100_segment_known) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A -> P0, B -> P1
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    run_comparison(provider, pp, mapping, cache, "Small Grid: 0b1100 (Segment Known)");
}

BOOST_AUTO_TEST_CASE(benchmark_small_1110_three_points_known) {
    setup_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A -> P0, B -> P1, C -> P3
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0));
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 1));
    BOOST_REQUIRE(mapping.try_apply_assignment(2, 3));
    run_comparison(provider, pp, mapping, cache, "Small Grid: 0b1110 (Three Points Known)");
}

// Large geometry setup benchmarks (9 Points)

BOOST_AUTO_TEST_CASE(benchmark_large_0000_brute_force) {
    setup_large_grid();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    run_comparison(provider, pp, mapping, cache, "Large Grid: 0b0000 (Brute Force)");
}

BOOST_AUTO_TEST_CASE(benchmark_large_1000_one_point) {
    setup_large_grid();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Center of the 3x3 grid (highly connected!)
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 4)); 
    run_comparison(provider, pp, mapping, cache, "Large Grid: 0b1000 (Center Point Known)");
}

BOOST_AUTO_TEST_CASE(benchmark_large_1100_segment_known) {
    setup_large_grid();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A and B to a length-1 segment in the grid
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 4)); // Center
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 5)); // Right
    run_comparison(provider, pp, mapping, cache, "Large Grid: 0b1100 (Segment Known)");
}

// Very large setup benchmarks (5x5 square - 25 points)

// This Currently severely underestimates because the provider uses an approximated average for pairs in a bucket 
// However when we have a few very large buckets, the actual result is higher. In the future we'll decide wether to 
// Have the cache remember bucket sizes or just have the estimate_extensions() function go over all buckets and get the size for each
// The latter shouldn't slow the provider down too much.
BOOST_AUTO_TEST_CASE(benchmark_very_large_0000_brute_force) {
    setup_very_large_grid();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    run_comparison(provider, pp, mapping, cache, "Very Large Grid 5x5: 0b0000 (Brute Force)");
}

// This Currently severely underestimates because the provider uses an approximated average for pairs in a bucket 
// However when we have a few very large buckets, the actual result is higher. In the future we'll decide wether to 
// Have the cache remember bucket sizes or just have the estimate_extensions() function go over all buckets and get the size for each
// The latter shouldn't slow the provider down too much.
BOOST_AUTO_TEST_CASE(benchmark_very_large_1000_one_point) {
    setup_very_large_grid();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Center of the 5x5 grid
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 12)); 
    run_comparison(provider, pp, mapping, cache, "Very Large Grid 5x5: 0b1000 (Center Point Known)");
}

BOOST_AUTO_TEST_CASE(benchmark_very_large_1100_segment_known) {
    setup_very_large_grid();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // Map A and B to a length-1 segment in the grid
    BOOST_REQUIRE(mapping.try_apply_assignment(0, 12)); // Center
    BOOST_REQUIRE(mapping.try_apply_assignment(1, 13)); // Right
    run_comparison(provider, pp, mapping, cache, "Very Large Grid 5x5: 0b1100 (Segment Known)");
}

// Irregular setup benchmarks

BOOST_AUTO_TEST_CASE(benchmark_irregular_0000_brute_force) {
    setup_irregular_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    // The generator should find 0 valid mappings on the irregular setup.
    // The estimate should also be low
    run_comparison(provider, pp, mapping, cache, "Irregular Geometry: 0b0000 (Brute Force)");
}

BOOST_AUTO_TEST_CASE(benchmark_irregular_1000_one_point) {
    setup_irregular_geometry();
    LazyGeometryCache cache(prob);
    MappingState mapping(schema, prob);
    PlannedPredicate pp = build_planned_pred({"A", "B", "C", "D"});

    BOOST_REQUIRE(mapping.try_apply_assignment(0, 0)); // Map to R0
    run_comparison(provider, pp, mapping, cache, "Irregular Geometry: 0b1000 (One Point Known)");
}

BOOST_AUTO_TEST_SUITE_END()
