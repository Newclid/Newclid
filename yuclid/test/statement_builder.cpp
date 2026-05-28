#define BOOST_TEST_MODULE statement_builder_test

#include <boost/test/unit_test.hpp>

#include "statement/statement_builder.hpp"
#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/equal_angles.hpp"
#include "statement/equal_line_angles.hpp"
#include "statement/para.hpp"
#include "statement/perp.hpp"
#include "statement/eqratio.hpp"
#include "statement/cyclic.hpp"
#include "statement/circumcenter.hpp"
#include "statement/similar_triangles.hpp"
#include "statement/congruent_triangles.hpp"
#include "statement/midpoint.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "statement/dist_eq.hpp"
#include "statement/squared_dist_eq.hpp"
#include "statement/same_clock.hpp"
#include "statement/obtuse_angle.hpp"
#include "statement/same_side.hpp"
#include "statement/diff_side.hpp"
#include "statement/line_angle_eq.hpp"
#include "typedef.hpp"
#include "type/point.hpp"
#include "problem.hpp"
#include <stdexcept>

using namespace std;
using namespace Yuclid;

struct StatementBuilderFixture {
    RuleMapping mapping;
    Problem prob;

    StatementBuilderFixture() {
        mapping.emplace("A", prob.add_point("P1", 0.0, 0.0));
        mapping.emplace("B", prob.add_point("P2", 1.0, 0.0));
        mapping.emplace("C", prob.add_point("P3", 0.0, 1.0));
        mapping.emplace("D", prob.add_point("P4", 1.0, 1.0));
        mapping.emplace("E", prob.add_point("P5", 2.0, 0.0));
        mapping.emplace("F", prob.add_point("P6", 0.0, 2.0));
        mapping.emplace("G", prob.add_point("P7", 2.0, 2.0));
        mapping.emplace("H", prob.add_point("P8", 3.0, 3.0));
    }

    template <typename ExpectedStatementType>
    void verify_results(const std::vector<std::unique_ptr<Statement>>& results, std::size_t expected_size) {
        static_assert(
            std::is_base_of_v<Statement, ExpectedStatementType>,"The resulting pointers must be have and expected type of Statement!"
        );

        BOOST_REQUIRE_EQUAL(results.size(), expected_size);

        for (std::size_t i = 0; i < results.size(); ++i) {
            BOOST_REQUIRE(results[i] != nullptr);
            
            auto* typed_statement = dynamic_cast<ExpectedStatementType*>(results[i].get());
            BOOST_CHECK_MESSAGE(typed_statement != nullptr, 
                                "Statement at index " << i << " was not of the expected type! " 
                                "Expected: " << typeid(ExpectedStatementType).name());
        }
    }
};

BOOST_FIXTURE_TEST_SUITE(statement_builder_suite, StatementBuilderFixture)

/**
 * @brief Test case for arity mismatch in schema definition
 * Verifies that the statement builder properly handles arity mismatch in schemas
 */
BOOST_AUTO_TEST_CASE(statement_builder_arity_mismatch) {
    RulePredicatePattern pattern = {"cong", {"A", "B", "C"}};
    // Verify it throws a runtime_error
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for undeclared variable
 * Verifies that the statement builder throws an exception when an argument is not in the mapping
 */
BOOST_AUTO_TEST_CASE(statement_builder_undeclared_variables) {
    RulePredicatePattern pattern = {"coll", {"X", "Y", "Z"}};
    // Verify it throws a runtime_error when it tries to call mapped_point() and fails to find "X"
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for unknown predicate type
 * Verifies that the statement builder throws an exception when an unknown predicate is encountered
 */
BOOST_AUTO_TEST_CASE(statement_builder_unknown_predicate) {
    // Make a pattern that doesn't exist (and hopefully wont be added in the future)
    RulePredicatePattern pattern = {"unknown_nonexistent_predicate", {"A", "B"}};
    // Verify it throws a runtime error
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern, mapping), std::runtime_error);
}

// Tests for each predicate

BOOST_AUTO_TEST_CASE(statement_builder_cong) {
    RulePredicatePattern pattern = {"cong", {"A", "B", "C", "D"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<DistEqDist>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_para) {
    RulePredicatePattern pattern = {"para", {"A", "B", "C", "D"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Parallel>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_perp) {
    RulePredicatePattern pattern = {"perp", {"A", "B", "C", "D"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Perpendicular>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_eqratio) {
    RulePredicatePattern pattern = {"eqratio", {"A", "B", "C", "D", "E", "F", "G", "H"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualRatios>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_midp) {
    RulePredicatePattern pattern = {"midp", {"A", "B", "C"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Midpoint>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_obtuse_angle) {
    RulePredicatePattern pattern = {"obtuse_angle", {"A", "B", "C"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<ObtuseAngle>(results, 1);
}


/**
 * @brief Test case angle equality
 * Verifies that the statement builder handles the variable arity
 */
BOOST_AUTO_TEST_CASE(statement_builder_eqangle_6_args) {
    RulePredicatePattern pattern = {"eqangle", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualAngles>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_eqangle_8_args) {
    RulePredicatePattern pattern = {"equal_angles", {"A", "B", "C", "D", "E", "F", "G", "H"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualLineAngles>(results, 1);
}

// Triangles

BOOST_AUTO_TEST_CASE(statement_builder_simtri) {
    RulePredicatePattern pattern = {"simtri", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SimilarTriangles>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_simtrir) {
    RulePredicatePattern pattern = {"simtrir", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SimilarTriangles>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_contri) {
    RulePredicatePattern pattern = {"contri", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<CongruentTriangles>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_contrir) {
    RulePredicatePattern pattern = {"contrir", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<CongruentTriangles>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_sameclock) {
    RulePredicatePattern pattern = {"sameclock", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SameClock>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_sameside) {
    RulePredicatePattern pattern = {"sameside", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SameSignDot>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_nsameside) {
    RulePredicatePattern pattern = {"nsameside", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<DiffSignDot>(results, 1);
}

/**
 * @brief Test case for rconst
 * Verifies that the statement builder properly handles the constants passed
 */
BOOST_AUTO_TEST_CASE(statement_builder_rconst) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "5/2"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<RatioDistEquals>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_r2const) {
    RulePredicatePattern pattern = {"r2const", {"A", "B", "C", "D", "3"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<RatioSquaredDist>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_lconst) {
    RulePredicatePattern pattern = {"lconst", {"A", "B", "3/2"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<DistEq>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_l2const) {
    RulePredicatePattern pattern = {"l2const", {"A", "B", "4"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SquaredDistEq>(results, 1);
}

BOOST_AUTO_TEST_CASE(statement_builder_aconst) {
    RulePredicatePattern pattern = {"aconst", {"A", "B", "C", "D", "-1"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<LineAngleEq>(results, 1);
}

// Multi-statement patterns

BOOST_AUTO_TEST_CASE(statement_builder_coll_rolling) {
    RulePredicatePattern pattern = {"coll", {"A", "B", "C", "D", "E"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Collinear>(results, 3); // (A,B,C); (B,C,D); (C,D,E)
}

BOOST_AUTO_TEST_CASE(statement_builder_cyclic_rolling) {
    RulePredicatePattern pattern = {"cyclic", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<CyclicQuadrangle>(results, 3); // (A,B,C,D); (B,C,D,E); (C,D,E,F)
}

BOOST_AUTO_TEST_CASE(statement_builder_circumcenter_rolling) {
    RulePredicatePattern pattern = {"circumcenter", {"A", "B", "C", "D", "E"}}; // A is the center
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Circumcenter>(results, 2); // (A, Tri(B,C,D)); (A, Tri(C,D,E))
}

BOOST_AUTO_TEST_SUITE_END()