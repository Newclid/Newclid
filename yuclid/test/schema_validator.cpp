#define BOOST_TEST_MODULE schema_validator_test

#include <boost/test/unit_test.hpp>
#include <string>
#include <vector>

#include "rules/schema_validator.hpp"
#include "rules/rule_schema.hpp"

using namespace std;
using namespace Yuclid;

struct SchemaValidatorFixture {
    
    // Helper to build a RuleSchema
    RuleSchema build_schema(
        const std::string& id,
        const std::vector<std::string>& vars,
        const std::vector<RulePredicatePattern>& hyps,
        const std::vector<RulePredicatePattern>& concs = {}
    ) {
        RuleSchema schema;
        schema.id = id;
        schema.variables = vars;
        schema.hypotheses = hyps;
        schema.conclusions = concs;
        return schema;
    }

    // Helper to assert a schema is perfectly valid
    void require_valid(const RuleSchema& schema) {
        auto result = SchemaValidator::validate(schema);
        BOOST_REQUIRE_MESSAGE(!result.has_value(), 
            "Schema was expected to be valid, but failed with: " << result.value_or(""));
    }

    // Helper to assert a schema fails, and optionally check the error message
    void require_invalid(const RuleSchema& schema, const std::string& expected_error_substring = "") {
        auto result = SchemaValidator::validate(schema);
        BOOST_REQUIRE_MESSAGE(result.has_value(), 
            "Schema was expected to be invalid, but passed validation!");
        
        if (!expected_error_substring.empty()) {
            BOOST_CHECK_MESSAGE(result.value().find(expected_error_substring) != std::string::npos,
                "Error message did not contain expected substring.\nExpected to find: " 
                << expected_error_substring << "\nActual error: " << result.value());
        }
    }
};

BOOST_FIXTURE_TEST_SUITE(schema_validator_suite, SchemaValidatorFixture)

/**
 * @brief Test exact arity success (4 arguments)
 */
BOOST_AUTO_TEST_CASE(validator_valid_exact_arity_4) {
    auto schema = build_schema("test_cong", {"A", "B", "C", "D"}, {
        {"cong", {"A", "B", "C", "D"}},
        {"para", {"A", "B", "C", "D"}},
        {"perp", {"A", "B", "C", "D"}}
    });
    require_valid(schema);
}

/**
 * @brief Test sliding window predicates (At least N arguments)
 */
BOOST_AUTO_TEST_CASE(validator_valid_sliding_window_coll_cyclic) {
    auto schema = build_schema("test_sliding", {"A", "B", "C", "D", "E"}, {
        {"coll", {"A", "B", "C", "D", "E"}},
        {"cyclic", {"A", "B", "C", "D", "E"}}
    });
    require_valid(schema);
}

/**
 * @brief Test overloaded arity (eqangle accepts exactly 6 or exactly 8)
 */
BOOST_AUTO_TEST_CASE(validator_valid_eqangle_overloads) {
    auto schema = build_schema("test_eqangle", {"A", "B", "C", "D", "E", "F", "G", "H"}, {
        {"eqangle", {"A", "B", "C", "D", "E", "F"}},             // 6 args
        {"equal_angles", {"A", "B", "C", "D", "E", "F", "G", "H"}} // 8 args
    });
    require_valid(schema);
}

/**
 * @brief Test strict exact arity success (6 and 8 arguments)
 */
BOOST_AUTO_TEST_CASE(validator_valid_exact_arity_large) {
    auto schema = build_schema("test_large_arity", {"A", "B", "C", "D", "E", "F", "G", "H"}, {
        {"simtri", {"A", "B", "C", "D", "E", "F"}},
        {"eqratio", {"A", "B", "C", "D", "E", "F", "G", "H"}}
    });
    require_valid(schema);
}

/**
 * @brief Test Legacy Constant Bypass
 * Verifies that the validator ignores the undeclared "1/2" string in the constant slot
 */
BOOST_AUTO_TEST_CASE(validator_valid_legacy_constant_bypass) {
    auto schema = build_schema("test_constants", {"A", "B", "C", "D"}, {
        {"rconst", {"A", "B", "C", "D", "1/2"}}, // "1/2" is not in vars, should pass
        {"lconst", {"A", "B", "3"}}              // "3" is not in vars, should pass
    });
    require_valid(schema);
}

/**
 * @brief Test unknown predicate rejection
 */
BOOST_AUTO_TEST_CASE(validator_invalid_unknown_predicate) {
    auto schema = build_schema("test_unknown", {"A", "B"}, {
        {"magic_geometry_rule", {"A", "B"}}
    });
    require_invalid(schema, "Unknown rule predicate");
}

/**
 * @brief Test too few arguments
 */
BOOST_AUTO_TEST_CASE(validator_invalid_arity_underflow) {
    auto schema_cong = build_schema("err", {"A", "B", "C"}, { {"cong", {"A", "B", "C"}} });
    require_invalid(schema_cong, "expects exactly 4");

    auto schema_coll = build_schema("err", {"A", "B"}, { {"coll", {"A", "B"}} });
    require_invalid(schema_coll, "expects at least 3");

    auto schema_eqangle = build_schema("err", {"A", "B", "C", "D", "E"}, { {"eqangle", {"A", "B", "C", "D", "E"}} });
    require_invalid(schema_eqangle, "expects either 6 or 8");
}

/**
 * @brief Test too many arguments for a strict predicate
 */
BOOST_AUTO_TEST_CASE(validator_invalid_arity_overflow) {
    // midp takes exactly 3, giving it 4 should fail
    auto schema_midp = build_schema("err", {"A", "B", "C", "D"}, { {"midp", {"A", "B", "C", "D"}} });
    require_invalid(schema_midp, "expects exactly 3");

    // eqangle takes 6 or 8. Giving it 7 should fail.
    auto schema_eqangle = build_schema("err", {"A", "B", "C", "D", "E", "F", "G"}, { {"eqangle", {"A", "B", "C", "D", "E", "F", "G"}} });
    require_invalid(schema_eqangle, "expects either 6 or 8");
}

/**
 * @brief Test Undeclared Variable in Hypothesis
 */
BOOST_AUTO_TEST_CASE(validator_invalid_undeclared_variable_hyp) {
    auto schema = build_schema("test_scope", {"A", "B", "C", "D"}, {
        {"cong", {"A", "B", "C", "X"}} 
    });
    require_invalid(schema, "is not declared");
}

/**
 * @brief Test Undeclared Variable in Conclusion
 */
BOOST_AUTO_TEST_CASE(validator_invalid_undeclared_variable_conc) {
    auto schema = build_schema("test_scope_conc", {"A", "B", "C"}, 
        { {"coll", {"A", "B", "C"}} },
        { {"midp", {"A", "Z", "C"}} }
    );
    require_invalid(schema, "is not declared");
}

/**
 * @brief Test Legacy Constant Bypass Failure
 * Verifies that if they put an undeclared variable in a NON-constant slot of rconst, it fails.
 */
BOOST_AUTO_TEST_CASE(validator_invalid_constant_wrong_slot) {
    // rconst expects (var, var, var, var, const). 
    // Here we put "1/2" in index 3 (a variable slot), and "D" in the const slot.
    auto schema = build_schema("test_bad_const", {"A", "B", "C", "D"}, {
        {"rconst", {"A", "B", "C", "1/2", "D"}} 
    });
    require_invalid(schema, "is not declared");
}

BOOST_AUTO_TEST_SUITE_END()