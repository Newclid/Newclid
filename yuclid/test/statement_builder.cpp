#define BOOST_TEST_MODULE statement_builder_test

#include <boost/test/unit_test.hpp>

#include "statement/statement_builder.hpp"
#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "config_options.hpp"
#include "solver/ddar_solver.hpp"
#include <stdexcept>

using namespace std;
using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(statement_builder_suite)

/**
 * @brief Test case for arity mismatch in schema definition
 * Verifies that the statement builder properly handles arity mismatch in schemas
 */
BOOST_AUTO_TEST_CASE(statement_builder_arity_mismatch) {
    RulePredicatePattern pattern = {"cong", {"X", "Y", "Z"}};
    
    // Empty mapping (Builder should fail before looking at points)
    RuleMapping mapping; 
    
    // Verify it throws a runtime_error
    BOOST_CHECK_THROW((void)build_statement_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for undeclared variable
 * Verifies that the statement builder throws an exception when an argument is not in the mapping
 */
BOOST_AUTO_TEST_CASE(statement_builder_undeclared_variables) {
    // Setup a valid pattern
    RulePredicatePattern pattern = {"coll", {"X", "Y", "Z"}};
    
    // Setup an empty mapping (Z, Y, and X are not declared)
    RuleMapping mapping;
    
    // Verify it throws a runtime_error when it tries to call mapped_point() and fails to find "X"
    BOOST_CHECK_THROW((void)build_statement_from_pattern(pattern, mapping), std::runtime_error);
}

/**
 * @brief Test case for unknown predicate type
 * Verifies that the statement builder throws an exception when an unknown predicate is encountered
 */
BOOST_AUTO_TEST_CASE(statement_builder_unknown_predicate) {
    // Make a pattern that doesn't exist (and hopefully wont be added in the future)
    RulePredicatePattern pattern = {"unknown_nonexistent_predicate", {"X", "Y"}};
    
    // Empty mapping
    RuleMapping mapping;
    
    // Verify it throws a runtime error
    BOOST_CHECK_THROW((void)build_statement_from_pattern(pattern, mapping), std::runtime_error);
}

BOOST_AUTO_TEST_SUITE_END()