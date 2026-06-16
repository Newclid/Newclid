#define BOOST_TEST_MODULE generic_matcher_test

#include <boost/test/unit_test.hpp>

#include "matchers/generic_rule_matcher.hpp"
#include "problem.hpp"
#include "rules/rule_schema.hpp"
#include "type/point.hpp"
#include "theorem.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include <vector>

using namespace std;
using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(generic_matcher_suite)

/**
 * A helper method to build simple schemas with one hypothesis and one conclusion
 * Returns the schema object that was created with the given arguments
 */
RuleSchema build_simple_schema(
    const std::string &schema_id,
    const std::vector<std::string> &variables,
    const std::string &hyp_name,
    const std::vector<std::string> &hyp_vars,
    const std::string &conc_name,
    const std::vector<std::string> &conc_vars
) {
    RuleSchema schema;
    schema.id = schema_id;
    schema.variables = variables;

    RulePredicatePattern hyp = {hyp_name, hyp_vars};
    schema.hypotheses.push_back(hyp);

    RulePredicatePattern conc = {conc_name, conc_vars};
    schema.conclusions.push_back(conc);

    return schema;
}

/**
 * @brief Test case for empty problem (no points)
 * Verifies that the generic matcher safely handles empty problem inputs
 */
BOOST_AUTO_TEST_CASE(generic_match_empty_problem) {
    Problem prob;
    
    // Create a schema for the custom rule
    RuleSchema schema = build_simple_schema(
        "empty_problem_test",
        {"X", "Y"},
        "cong",
        {"X", "Y", "X", "Y"},
        "cong",
        {"Y", "X", "Y", "X"}
    );
    
    std::vector<RuleSchema> rules = { schema };
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Assert that there are no results
    BOOST_REQUIRE_EQUAL(results.size(), 0);
}

/**
 * @brief Test case for no schemas in vector
 * Verifies that the generic matcher safely handles the pass of an empty vector
 */
BOOST_AUTO_TEST_CASE(generic_match_empty_vector_schemas){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    
    // Create an empty vector
    std::vector<RuleSchema> rules = {};
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Assert that there are no results
    BOOST_REQUIRE_EQUAL(results.size(), 0);
}

/**
 * @brief Test case for a partially true schema
 * Verifies that the generic matcher doesnt match schemas for which only some hypotheses are true
 */
BOOST_AUTO_TEST_CASE(generic_match_partially_true_schema){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    (void)prob.add_point("P3", 0.0, 1.0);
    
    // Create a schema for the custom rule
    RuleSchema schema_false = build_simple_schema(
        "partially_true_schema",
        {"X", "Y", "Z"},
        "coll",
        {"X", "Y", "Z"},
        "coll",
        {"Z", "Y", "X"}
    );

    // Add second hypothesis, this one is true for the 3 points given
    RulePredicatePattern hyp = {"cong", {"X", "Y", "X", "Y"}};
    schema_false.hypotheses.push_back(hyp);

    std::vector<RuleSchema> rules = { schema_false };
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Assert that there are no results
    BOOST_REQUIRE_EQUAL(results.size(), 0);
}

/**
 * @brief Test case for normalization
 * Verifies that the generic matcher normalizes the results
 */
BOOST_AUTO_TEST_CASE(generic_match_normalization){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    (void)prob.add_point("P3", 2.0, 0.0);
    
    // Create a schema for the custom rule
    RuleSchema schema_norm = build_simple_schema(
        "normalization_schema",
        {"X", "Y", "Z"},
        "coll",
        {"X", "Y", "Z"},
        "coll",
        {"Z", "Y", "X"}
    );

    std::vector<RuleSchema> rules = { schema_norm };
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Assert number of results
    BOOST_REQUIRE_EQUAL(results.size(), 6);

    // Check every theorem in the result
    for (const auto& theorem : results) {
        // Cast the conclusion to the expected statement (coll)
        const Statement* base_statement = theorem.conclusions()[0].get();
        const Collinear* coll_statement = dynamic_cast<const Collinear*>(base_statement);
        
        BOOST_REQUIRE(coll_statement != nullptr);
        std::vector<Point> pts = coll_statement->points();
        BOOST_REQUIRE_EQUAL(pts.size(), 3);
        
        // All conclusions must be chronologically sorted
        BOOST_CHECK(pts[0] < pts[1]);
        BOOST_CHECK(pts[1] < pts[2]);
    }
}

/**
 * @brief Test case for an insufficient number of points in problem
 * Verifies that the generic matcher properly handles cases where the schema passed requires more points then there are in the problem
 */
BOOST_AUTO_TEST_CASE(generic_match_insufficient_points){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    
    // Create a schema for the custom rule
    RuleSchema schema_false = build_simple_schema(
        "schema_with_more_vars_than_problem_points",
        {"X", "Y", "Z"},
        "coll",
        {"X", "Y", "Z"},
        "coll",
        {"X", "Y", "Z"}
    );

    std::vector<RuleSchema> rules = { schema_false };
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Assert that there are no results
    BOOST_REQUIRE_EQUAL(results.size(), 0);
}

/**
 * @brief Test case for a single schema that successfully matches the problem points
 * Verifies that the generic matcher returns a correct output when a passed schema results in 'correct' theorems
 */
BOOST_AUTO_TEST_CASE(generic_match_successfull_match){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    (void)prob.add_point("P3", 0.0, 1.0);
    (void)prob.add_point("P4", 1.0, 1.0);
    (void)prob.add_point("P5", 5.0, 0.0);
    
    // Create a schema for the custom rule
    // This rule will identify all sets of 4 points forming a rhombus and conclude that the sides are parallel
    RuleSchema passing_schema = build_simple_schema(
        "passing_schema",
        {"X", "Y", "Z", "W"},
        "cong",
        {"X", "Y", "X", "Z"},
        "para",
        {"X", "Y", "Z", "W"}
    );

    RulePredicatePattern hyp2 = {"cong", {"X", "Z", "Z", "W"}};
    passing_schema.hypotheses.push_back(hyp2);

    RulePredicatePattern hyp3 = {"cong", {"Z", "W", "W", "Y"}};
    passing_schema.hypotheses.push_back(hyp3);

    RulePredicatePattern conc2 = {"para", {"X", "Z", "Y", "W"}};
    passing_schema.conclusions.push_back(conc2);

    std::vector<RuleSchema> rules = { passing_schema };
    
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Check the number of theorems is as expected
    BOOST_REQUIRE_EQUAL(results.size(), 8);
}

/**
 * @brief Test case for multiple schemas
 * Verifies that the generic matcher otputs correct results, when there are multiple schemas some of which that don't result in any true theorems, while others are poor/incompatible
 */
BOOST_AUTO_TEST_CASE(generic_match_mixed_schemas){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    (void)prob.add_point("P3", 0.0, 1.0);
    
    // Create a schema for the custom rule
    // This rule will identify all sets of 4 points forming a rhombus and conclude that the sides are parallel
    RuleSchema hyp_fail_numeric_check_schema = build_simple_schema(
        "hyp_fail_numeric_schema",
        {"X", "Y", "Z"},
        "coll",
        {"X", "Y", "Z"},
        "cong",
        {"X", "Y", "X", "Z"}
    );

    RuleSchema conc_fail_numeric_check_schema = build_simple_schema(
        "conc_fail_numeric_schema",
        {"X", "Y", "Z"},
        "cong",
        {"X", "Y", "X", "Z"},
        "coll",
        {"X", "Y", "Z"}
    );

    RuleSchema trivially_true_schema = build_simple_schema(
        "trivially_true_schema",
        {"X", "Y"},
        "cong",
        {"X", "Y", "X", "Y"},
        "cong",
        {"Y", "X", "Y", "X"}
    );

    std::vector<RuleSchema> rules = { 
        hyp_fail_numeric_check_schema, 
        conc_fail_numeric_check_schema, 
        trivially_true_schema 
    };
    
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.match();
    
    // Check the number of theorems is as expected
    BOOST_REQUIRE_EQUAL(results.size(), 6);

    // Check that only schema three produced theorems
    for(const auto& result: results){
        BOOST_CHECK_EQUAL(result.name(), trivially_true_schema.id);
    }
}



/**
 * @brief Test case for schemas with more variables than points in the problem
 * Verifies that the optimized generic matcher skips schemas that it cannot fully map because of insufficient points in the problem
 */
BOOST_AUTO_TEST_CASE(generic_match_optimized_skip_when_insufficient_points){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    (void)prob.add_point("P3", 2.0, 0.0);
    
    // Create a schema for the custom rule
    RuleSchema schema_false = build_simple_schema(
        "long_schema",
        {"X", "Y", "Z", "W"},
        "coll",
        {"X", "Y", "Z"},
        "coll",
        {"W", "Y", "X"}
    );

    std::vector<RuleSchema> rules = { schema_false };
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.optimized_match();
    
    // Assert that there are no results
    BOOST_REQUIRE_EQUAL(results.size(), 0);
}

/**
 * @brief Test case for schemas with unsupported predicates
 * Verifies that the optimized generic matcher skips schemas with unsupported predicates in them
 */
BOOST_AUTO_TEST_CASE(generic_match_optimized_skip_unsupported){
    Problem prob;
    (void)prob.add_point("P1", 0.0, 0.0);
    (void)prob.add_point("P2", 1.0, 0.0);
    (void)prob.add_point("P3", 2.0, 0.0);
    
    // Create a schema for the custom rule
    RuleSchema schema_norm = build_simple_schema(
        "normal_schema",
        {"X", "Y", "Z"},
        "unsupported_predicate_1",
        {"X", "Y", "Z"},
        "unsupported_predicate_2",
        {"Z", "Y", "X"}
    );

    std::vector<RuleSchema> rules = { schema_norm };
    
    // Build the matcher and call it
    GenericRuleMatcher matcher(&prob, rules);
    std::vector<Theorem> results = matcher.optimized_match();
    
    // Assert number of results
    BOOST_REQUIRE_EQUAL(results.size(), 0);
}


BOOST_AUTO_TEST_SUITE_END()