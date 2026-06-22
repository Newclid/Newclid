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

BOOST_AUTO_TEST_SUITE_END()