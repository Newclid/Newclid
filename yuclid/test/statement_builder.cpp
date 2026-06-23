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
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <string>
#include <system_error>
#include <type_traits>
#include <typeinfo>
#include <variant>
#include <vector>

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

    void verify_point_mapping(const std::unique_ptr<Statement>& result_statement, const std::vector<std::string>& expected_point_order) {
        std::vector<Point> result_points = result_statement->points();

        BOOST_REQUIRE(result_points.size() == expected_point_order.size());

        for(std::size_t i = 0; i < result_points.size(); ++i){
            BOOST_REQUIRE(result_points[i] == mapping.at(expected_point_order[i]));
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

/**
 * @brief Test case for arity mismatch for sliding window predicate cyclic
 * Verifies that the statement builder throws an error when 3 variables are passed instead of the minimum 4
 */
BOOST_AUTO_TEST_CASE(statement_builder_cyclic_underflow) {
    RulePredicatePattern pattern = {"cyclic", {"A", "B", "C"}};
    
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for arity mismatch for sliding window predicate coll
 * Verifies that the statement builder throws an error when 2 variables are passed instead of the minimum 3
 */
BOOST_AUTO_TEST_CASE(statement_builder_coll_underflow) {
    RulePredicatePattern pattern = {"coll", {"A", "B"}};
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for arity mismatch for sliding window predicate circumcenter
 * Verifies that the statement builder throws an error when 3 variables are passed instead of the minimum 4
 */
BOOST_AUTO_TEST_CASE(statement_builder_circumcenter_underflow) {
    RulePredicatePattern pattern = {"circumcenter", {"A", "B", "C"}};
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for arity mismatch for the two cases for equangle
 * Verifies that the statement builder throws an error when the number of variables is insufficient and on the border of the accepted arity
 */
BOOST_AUTO_TEST_CASE(statement_builder_eqangle_invalid_arity) {
    RulePredicatePattern pattern_7 = {"eqangle", {"A", "B", "C", "D", "E", "F", "G"}};
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern_7, mapping), std::runtime_error);
    
    RulePredicatePattern pattern_5 = {"eqangle", {"A", "B", "C", "D", "E"}};
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern_5, mapping), std::runtime_error);
}

/**
 * @brief Test case for arity mismatch for the predicates that expect a constant
 * Verifies that the statement builder throws an error when a constant isnt provided or when there are extra variables listed after it
 */
BOOST_AUTO_TEST_CASE(statement_builder_rconst_invalid_arity) {
    RulePredicatePattern pattern_under = {"rconst", {"A", "B", "C", "D"}};
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern_under, mapping), std::runtime_error);
    
    RulePredicatePattern pattern_over = {"rconst", {"A", "B", "C", "D", "5", "A"}};
    BOOST_CHECK_THROW((void)build_statements_from_pattern(pattern_over, mapping), std::runtime_error);
}


// Tests for each predicate

BOOST_AUTO_TEST_CASE(statement_builder_cong) {
    RulePredicatePattern pattern = {"cong", {"A", "B", "C", "D"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<DistEqDist>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_para) {
    RulePredicatePattern pattern = {"para", {"A", "B", "C", "D"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Parallel>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_perp) {
    RulePredicatePattern pattern = {"perp", {"A", "B", "C", "D"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Perpendicular>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_eqratio) {
    RulePredicatePattern pattern = {"eqratio", {"A", "B", "C", "D", "E", "F", "G", "H"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualRatios>(results, 1);
    
    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F", "G", "H"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_midp) {
    RulePredicatePattern pattern = {"midp", {"A", "B", "C"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Midpoint>(results, 1);
    
    std::vector<string> expected_order = {"B", "A", "C"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_obtuse_angle) {
    RulePredicatePattern pattern = {"obtuse_angle", {"A", "B", "C"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<ObtuseAngle>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C"};
    verify_point_mapping(results[0], expected_order);
}


/**
 * @brief Test case angle equality
 * Verifies that the statement builder handles the variable arity
 */
BOOST_AUTO_TEST_CASE(statement_builder_eqangle_6_args) {
    RulePredicatePattern pattern = {"eqangle", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualAngles>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_eqangle_8_args) {
    RulePredicatePattern pattern = {"equal_angles", {"A", "B", "C", "D", "E", "F", "G", "H"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualLineAngles>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F", "G", "H"};
    verify_point_mapping(results[0], expected_order);
}

// Triangles

BOOST_AUTO_TEST_CASE(statement_builder_simtri) {
    RulePredicatePattern pattern = {"simtri", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SimilarTriangles>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);

    BOOST_REQUIRE(results[0]->name() == "simtri");
}

BOOST_AUTO_TEST_CASE(statement_builder_simtrir) {
    RulePredicatePattern pattern = {"simtrir", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SimilarTriangles>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);

    BOOST_REQUIRE(results[0]->name() == "simtrir");
}

BOOST_AUTO_TEST_CASE(statement_builder_contri) {
    RulePredicatePattern pattern = {"contri", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<CongruentTriangles>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);

    BOOST_REQUIRE(results[0]->name() == "contri");
}

BOOST_AUTO_TEST_CASE(statement_builder_contrir) {
    RulePredicatePattern pattern = {"contrir", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<CongruentTriangles>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);

    BOOST_REQUIRE(results[0]->name() == "contrir");
}

BOOST_AUTO_TEST_CASE(statement_builder_sameclock) {
    RulePredicatePattern pattern = {"sameclock", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SameClock>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_sameside) {
    RulePredicatePattern pattern = {"sameside", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SameSignDot>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);
}

BOOST_AUTO_TEST_CASE(statement_builder_nsameside) {
    RulePredicatePattern pattern = {"nsameside", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<DiffSignDot>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D", "E", "F"};
    verify_point_mapping(results[0], expected_order);
}

/**
 * @brief Test case for rconst
 * Verifies that the statement builder properly handles the constants passed
 */
BOOST_AUTO_TEST_CASE(statement_builder_rconst) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "5/2"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<RatioDistEquals>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);

    auto* result_ptr = dynamic_cast<RatioDistEquals*>(results[0].get());
    BOOST_REQUIRE_MESSAGE(result_ptr->ratio() == NNRat(5, 2), 
                    "The resulting ratio  " << result_ptr->ratio()
                    << "did not match the expected ratio " << NNRat(5, 2));
}

BOOST_AUTO_TEST_CASE(statement_builder_r2const) {
    RulePredicatePattern pattern = {"r2const", {"A", "B", "C", "D", "3/1"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<RatioSquaredDist>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);

    auto* result_ptr = dynamic_cast<RatioSquaredDist*>(results[0].get());
    BOOST_REQUIRE_MESSAGE(result_ptr->ratio() == NNRat(3, 1), 
                "The resulting ratio  " << result_ptr->ratio()
                << "did not match the expected ratio " << NNRat(3,1));
}

BOOST_AUTO_TEST_CASE(statement_builder_lconst) {
    RulePredicatePattern pattern = {"lconst", {"A", "B", "3/2"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<DistEq>(results, 1);

    std::vector<string> expected_order = {"A", "B"};
    verify_point_mapping(results[0], expected_order);

    auto* result_ptr = dynamic_cast<DistEq*>(results[0].get());
    auto args = result_ptr->args();
    // The ratio is the second item in the vector returned by args()
    NNRat actual_ratio = std::get<NNRat>(args[1]);

    BOOST_REQUIRE_MESSAGE(actual_ratio == NNRat(3, 2), 
                "The resulting ratio  " << actual_ratio
                << "did not match the expected ratio " << NNRat(3, 2));
}

BOOST_AUTO_TEST_CASE(statement_builder_l2const) {
    RulePredicatePattern pattern = {"l2const", {"A", "B", "42/1"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<SquaredDistEq>(results, 1);

    std::vector<string> expected_order = {"A", "B"};
    verify_point_mapping(results[0], expected_order);

    auto* result_ptr = dynamic_cast<SquaredDistEq*>(results[0].get());
    auto args = result_ptr->args();
    // The ratio is the second item in the vector returned by args()
    NNRat actual_ratio = std::get<NNRat>(args[1]);

    BOOST_REQUIRE_MESSAGE(actual_ratio == NNRat(42,1), 
            "The resulting ratio  " << actual_ratio
            << "did not match the expected ratio " << NNRat(42,1));
}

BOOST_AUTO_TEST_CASE(statement_builder_aconst) {
    RulePredicatePattern pattern = {"aconst", {"A", "B", "C", "D", "1/2"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<LineAngleEq>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);
    
    auto* result_ptr = dynamic_cast<LineAngleEq*>(results[0].get());
    auto args = result_ptr->args();
    // The third argument is an object of type AddCircle<Rat> so the ratio is extracted with the .number() method
    AddCircle<Rat> circle_val = std::get<AddCircle<Rat>>(args[2]);
    Rat actual_ratio = circle_val.number();

    // The ratio is normalized
    BOOST_REQUIRE_MESSAGE(actual_ratio == Rat(1, 2), 
            "The resulting ratio  " << actual_ratio
            << "did not match the expected ratio " << Rat(1, 2));
}

BOOST_AUTO_TEST_CASE(statement_builder_normalize_aconst) {
    RulePredicatePattern pattern = {"aconst", {"A", "B", "C", "D", "-1/3"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<LineAngleEq>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);
    
    auto* result_ptr = dynamic_cast<LineAngleEq*>(results[0].get());
    auto args = result_ptr->args();
    // The third argument is an object of type AddCircle<Rat> so the ratio is extracted with the .number() method
    AddCircle<Rat> circle_val = std::get<AddCircle<Rat>>(args[2]);
    Rat actual_ratio = circle_val.number();

    // The ratio is normalized so -1/2 turns into 2/3 (rotations on a circle)
    BOOST_REQUIRE_MESSAGE(actual_ratio == Rat(2, 3), 
            "The resulting ratio  " << actual_ratio
            << "did not match the expected ratio " << Rat(2, 3));
}

BOOST_AUTO_TEST_CASE(statement_builder_whole_number_gets_default_value) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "5"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<RatioDistEquals>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);

    auto* result_ptr = dynamic_cast<RatioDistEquals*>(results[0].get());
    BOOST_REQUIRE_MESSAGE(result_ptr->ratio() == NNRat(0,1), 
                    "The resulting ratio  " << result_ptr->ratio()
                    << "did not match the expected ratio " << NNRat(0,1));
}

BOOST_AUTO_TEST_CASE(statement_builder_div_by_zero_gets_default_value) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "12/0"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<RatioDistEquals>(results, 1);

    std::vector<string> expected_order = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order);

    auto* result_ptr = dynamic_cast<RatioDistEquals*>(results[0].get());
    BOOST_REQUIRE_MESSAGE(result_ptr->ratio() == NNRat(0,1), 
                    "The resulting ratio  " << result_ptr->ratio()
                    << "did not match the expected ratio " << NNRat(0,1));
}


// Bad constants in pattern

BOOST_AUTO_TEST_CASE(statement_builder_bad_const_denom) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "5/abc"}};
    
    BOOST_CHECK_THROW(
        (void)build_statements_from_pattern(pattern, mapping), 
        std::system_error
    );
}

BOOST_AUTO_TEST_CASE(statement_builder_bad_const_num) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "a/5"}};
    
    BOOST_CHECK_THROW(
        (void)build_statements_from_pattern(pattern, mapping), 
        std::system_error
    );
}

BOOST_AUTO_TEST_CASE(statement_builder_bad_const_end) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "5/"}};
    
    BOOST_CHECK_THROW(
        (void)build_statements_from_pattern(pattern, mapping), 
        std::system_error
    );
}

BOOST_AUTO_TEST_CASE(statement_builder_bad_const_start) {
    RulePredicatePattern pattern = {"rconst", {"A", "B", "C", "D", "/5"}};
    
    BOOST_CHECK_THROW(
        (void)build_statements_from_pattern(pattern, mapping), 
        std::system_error
    );
}

// Multi-statement patterns

BOOST_AUTO_TEST_CASE(statement_builder_coll_rolling) {
    RulePredicatePattern pattern = {"coll", {"A", "B", "C", "D", "E"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Collinear>(results, 3); // (A,B,C); (B,C,D); (C,D,E)
    
    std::vector<string> expected_order_1 = {"A", "B", "C"};
    verify_point_mapping(results[0], expected_order_1);

    std::vector<string> expected_order_2 = {"B", "C", "D"};
    verify_point_mapping(results[1], expected_order_2);

    std::vector<string> expected_order_3 = {"C", "D", "E"};
    verify_point_mapping(results[2], expected_order_3);
}

BOOST_AUTO_TEST_CASE(statement_builder_cyclic_rolling) {
    RulePredicatePattern pattern = {"cyclic", {"A", "B", "C", "D", "E", "F"}};
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<CyclicQuadrangle>(results, 3); // (A,B,C,D); (B,C,D,E); (C,D,E,F)

    std::vector<string> expected_order_1 = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order_1);

    std::vector<string> expected_order_2 = {"B", "C", "D", "E"};
    verify_point_mapping(results[1], expected_order_2);

    std::vector<string> expected_order_3 = {"C", "D", "E", "F"};
    verify_point_mapping(results[2], expected_order_3);
}

BOOST_AUTO_TEST_CASE(statement_builder_circumcenter_rolling) {
    RulePredicatePattern pattern = {"circumcenter", {"A", "B", "C", "D", "E"}}; // A is the center
    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Circumcenter>(results, 2); // (A, Tri(B,C,D)); (A, Tri(C,D,E))

    std::vector<string> expected_order_1 = {"A", "B", "C", "D"};
    verify_point_mapping(results[0], expected_order_1);

    std::vector<string> expected_order_2 = {"A", "C", "D", "E"};
    verify_point_mapping(results[1], expected_order_2);
}

/**
 * @brief Test both supported names for 6-argument angle equality.
 */
BOOST_AUTO_TEST_CASE(statement_builder_equal_angles_alias_6_args) {
    RulePredicatePattern pattern = {
        "equal_angles",
        {"A", "B", "C", "D", "E", "F"}
    };

    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualAngles>(results, 1);

    std::vector<std::string> expected_order = {
        "A", "B", "C", "D", "E", "F"
    };

    verify_point_mapping(results[0], expected_order);
}

/**
 * @brief Test the eqangle name for 8-argument line-angle equality.
 */
BOOST_AUTO_TEST_CASE(statement_builder_eqangle_8_arg_name) {
    RulePredicatePattern pattern = {
        "eqangle",
        {"A", "B", "C", "D", "E", "F", "G", "H"}
    };

    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<EqualLineAngles>(results, 1);

    std::vector<std::string> expected_order = {
        "A", "B", "C", "D", "E", "F", "G", "H"
    };

    verify_point_mapping(results[0], expected_order);
}

/**
 * @brief Test that circle is accepted as an alias for circumcenter.
 */
BOOST_AUTO_TEST_CASE(statement_builder_circle_alias_rolling) {
    RulePredicatePattern pattern = {
        "circle",
        {"A", "B", "C", "D", "E"}
    };

    auto results = build_statements_from_pattern(pattern, mapping);
    verify_results<Circumcenter>(results, 2);

    std::vector<std::string> expected_order_1 = {
        "A", "B", "C", "D"
    };

    verify_point_mapping(results[0], expected_order_1);

    std::vector<std::string> expected_order_2 = {
        "A", "C", "D", "E"
    };

    verify_point_mapping(results[1], expected_order_2);
}

/**
 * @brief All fixed-arity predicates reject malformed argument counts.
 */
BOOST_AUTO_TEST_CASE(statement_builder_fixed_arity_predicates_reject_wrong_arity) {
    const std::vector<RulePredicatePattern> bad_patterns = {
        {"para", {"A", "B", "C"}},
        {"perp", {"A", "B", "C"}},
        {"eqratio", {"A", "B", "C", "D", "E", "F", "G"}},

        {"simtri", {"A", "B", "C", "D", "E"}},
        {"simtrir", {"A", "B", "C", "D", "E"}},
        {"contri", {"A", "B", "C", "D", "E"}},
        {"contrir", {"A", "B", "C", "D", "E"}},

        {"midp", {"A", "B"}},
        {"obtuse_angle", {"A", "B"}},

        {"sameclock", {"A", "B", "C", "D", "E"}},
        {"sameside", {"A", "B", "C", "D", "E"}},
        {"nsameside", {"A", "B", "C", "D", "E"}},

        {"r2const", {"A", "B", "C", "D"}},
        {"lconst", {"A", "B"}},
        {"l2const", {"A", "B"}},
        {"aconst", {"A", "B", "C", "D"}},
    };

    for (const RulePredicatePattern& pattern : bad_patterns) {
        BOOST_TEST_CONTEXT("predicate: " << pattern.name) {
            BOOST_CHECK_THROW(
                (void)build_statements_from_pattern(pattern, mapping),
                std::runtime_error
            );
        }
    }
}

/**
 * @brief Legacy silent constant parsing defaults are preserved for all
 * constant predicate families.
 *
 * Inputs without a slash, such as "3", and division-by-zero inputs, such as
 * "2/0", currently parse to the default value 0/1.
 */
BOOST_AUTO_TEST_CASE(statement_builder_silent_default_constants_all_families) {
    const std::vector<std::string> default_values = {
        "3",
        "2/0",
    };

    for (const std::string& value : default_values) {
        BOOST_TEST_CONTEXT("rconst value: " << value) {
            RulePredicatePattern pattern = {
                "rconst",
                {"A", "B", "C", "D", value}
            };

            auto results = build_statements_from_pattern(pattern, mapping);
            verify_results<RatioDistEquals>(results, 1);

            auto* result_ptr =
                dynamic_cast<RatioDistEquals*>(results[0].get());

            BOOST_REQUIRE(result_ptr != nullptr);
            BOOST_CHECK(result_ptr->ratio() == NNRat(0, 1));
        }

        BOOST_TEST_CONTEXT("r2const value: " << value) {
            RulePredicatePattern pattern = {
                "r2const",
                {"A", "B", "C", "D", value}
            };

            auto results = build_statements_from_pattern(pattern, mapping);
            verify_results<RatioSquaredDist>(results, 1);

            auto* result_ptr =
                dynamic_cast<RatioSquaredDist*>(results[0].get());

            BOOST_REQUIRE(result_ptr != nullptr);
            BOOST_CHECK(result_ptr->ratio() == NNRat(0, 1));
        }

        BOOST_TEST_CONTEXT("lconst value: " << value) {
            RulePredicatePattern pattern = {
                "lconst",
                {"A", "B", value}
            };

            auto results = build_statements_from_pattern(pattern, mapping);
            verify_results<DistEq>(results, 1);

            auto* result_ptr =
                dynamic_cast<DistEq*>(results[0].get());

            BOOST_REQUIRE(result_ptr != nullptr);

            const auto args = result_ptr->args();
            const NNRat actual_ratio =
                std::get<NNRat>(args[1]);

            BOOST_CHECK(actual_ratio == NNRat(0, 1));
        }

        BOOST_TEST_CONTEXT("l2const value: " << value) {
            RulePredicatePattern pattern = {
                "l2const",
                {"A", "B", value}
            };

            auto results = build_statements_from_pattern(pattern, mapping);
            verify_results<SquaredDistEq>(results, 1);

            auto* result_ptr =
                dynamic_cast<SquaredDistEq*>(results[0].get());

            BOOST_REQUIRE(result_ptr != nullptr);

            const auto args = result_ptr->args();
            const NNRat actual_ratio =
                std::get<NNRat>(args[1]);

            BOOST_CHECK(actual_ratio == NNRat(0, 1));
        }

        BOOST_TEST_CONTEXT("aconst value: " << value) {
            RulePredicatePattern pattern = {
                "aconst",
                {"A", "B", "C", "D", value}
            };

            auto results = build_statements_from_pattern(pattern, mapping);
            verify_results<LineAngleEq>(results, 1);

            auto* result_ptr =
                dynamic_cast<LineAngleEq*>(results[0].get());

            BOOST_REQUIRE(result_ptr != nullptr);

            const auto args = result_ptr->args();
            const AddCircle<Rat> circle_value =
                std::get<AddCircle<Rat>>(args[2]);

            BOOST_CHECK(circle_value.number() == Rat(0, 1));
        }
    }
}

/**
 * @brief Malformed constants throw for every constant predicate family.
 */
BOOST_AUTO_TEST_CASE(statement_builder_bad_constants_all_families) {
    const std::vector<std::string> bad_values = {
        "5/",
        "/5",
        "5/abc",
        "a/5",
    };

    for (const std::string& value : bad_values) {
        BOOST_TEST_CONTEXT("rconst value: " << value) {
            RulePredicatePattern pattern = {
                "rconst",
                {"A", "B", "C", "D", value}
            };

            BOOST_CHECK_THROW(
                (void)build_statements_from_pattern(pattern, mapping),
                std::system_error
            );
        }

        BOOST_TEST_CONTEXT("r2const value: " << value) {
            RulePredicatePattern pattern = {
                "r2const",
                {"A", "B", "C", "D", value}
            };

            BOOST_CHECK_THROW(
                (void)build_statements_from_pattern(pattern, mapping),
                std::system_error
            );
        }

        BOOST_TEST_CONTEXT("lconst value: " << value) {
            RulePredicatePattern pattern = {
                "lconst",
                {"A", "B", value}
            };

            BOOST_CHECK_THROW(
                (void)build_statements_from_pattern(pattern, mapping),
                std::system_error
            );
        }

        BOOST_TEST_CONTEXT("l2const value: " << value) {
            RulePredicatePattern pattern = {
                "l2const",
                {"A", "B", value}
            };

            BOOST_CHECK_THROW(
                (void)build_statements_from_pattern(pattern, mapping),
                std::system_error
            );
        }

        BOOST_TEST_CONTEXT("aconst value: " << value) {
            RulePredicatePattern pattern = {
                "aconst",
                {"A", "B", "C", "D", value}
            };

            BOOST_CHECK_THROW(
                (void)build_statements_from_pattern(pattern, mapping),
                std::system_error
            );
        }
    }
}

BOOST_AUTO_TEST_SUITE_END()
