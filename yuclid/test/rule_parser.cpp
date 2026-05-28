#define BOOST_TEST_MODULE rule_parser_tests
#include <boost/test/unit_test.hpp>

#include <sstream>
#include <stdexcept>

#include "parser/rule_parser.hpp"

using namespace Yuclid;

/** These tests cover the separate user-defined rule schema parser, not the existing
 * Newclid/Yuclid JGEX problem parser. The input uses our proposed custom rule
 * syntax and only checks that parse_rule_schemas(...) converts text into
 * RuleSchema objects; predicate validation and conversion to real Statements happen later.
 * Rule format:
 * 
 * rule <rule_id> <variable1> <variable2> ...
 * require <predicate_name> <arg1> <arg2> ...
 * require <predicate_name> <arg1> <arg2> ...
 * conclude <predicate_name> <arg1> <arg2> ...
 * conclude <predicate_name> <arg1> <arg2> ...
 * end
 *
 * Require and conclude sections are independ number of each other
*/

BOOST_AUTO_TEST_SUITE(rule_parser_suite)

BOOST_AUTO_TEST_CASE(parse_single_rule) {
    std::istringstream input(R"(
        rule user_iso O A B
        require cong O A O B
        require ncoll O A B
        conclude eqangle O A B A B O
        end
    )");

    std::vector<RuleSchema> rules = parse_rule_schemas(input);

    BOOST_REQUIRE_EQUAL(rules.size(), 1);

    const RuleSchema &rule = rules.at(0);

    BOOST_CHECK_EQUAL(rule.id, "user_iso");

    BOOST_REQUIRE_EQUAL(rule.variables.size(), 3);
    BOOST_CHECK_EQUAL(rule.variables.at(0), "O");
    BOOST_CHECK_EQUAL(rule.variables.at(1), "A");
    BOOST_CHECK_EQUAL(rule.variables.at(2), "B");

    BOOST_REQUIRE_EQUAL(rule.hypotheses.size(), 2);

    BOOST_CHECK_EQUAL(rule.hypotheses.at(0).name, "cong");
    BOOST_REQUIRE_EQUAL(rule.hypotheses.at(0).args.size(), 4);
    BOOST_CHECK_EQUAL(rule.hypotheses.at(0).args.at(0), "O");
    BOOST_CHECK_EQUAL(rule.hypotheses.at(0).args.at(1), "A");
    BOOST_CHECK_EQUAL(rule.hypotheses.at(0).args.at(2), "O");
    BOOST_CHECK_EQUAL(rule.hypotheses.at(0).args.at(3), "B");

    BOOST_CHECK_EQUAL(rule.hypotheses.at(1).name, "ncoll");
    BOOST_REQUIRE_EQUAL(rule.hypotheses.at(1).args.size(), 3);
    BOOST_CHECK_EQUAL(rule.hypotheses.at(1).args.at(0), "O");
    BOOST_CHECK_EQUAL(rule.hypotheses.at(1).args.at(1), "A");
    BOOST_CHECK_EQUAL(rule.hypotheses.at(1).args.at(2), "B");

    BOOST_REQUIRE_EQUAL(rule.conclusions.size(), 1);

    BOOST_CHECK_EQUAL(rule.conclusions.at(0).name, "eqangle");
    BOOST_REQUIRE_EQUAL(rule.conclusions.at(0).args.size(), 6);
    BOOST_CHECK_EQUAL(rule.conclusions.at(0).args.at(0), "O");
    BOOST_CHECK_EQUAL(rule.conclusions.at(0).args.at(1), "A");
    BOOST_CHECK_EQUAL(rule.conclusions.at(0).args.at(2), "B");
    BOOST_CHECK_EQUAL(rule.conclusions.at(0).args.at(3), "A");
    BOOST_CHECK_EQUAL(rule.conclusions.at(0).args.at(4), "B");
    BOOST_CHECK_EQUAL(rule.conclusions.at(0).args.at(5), "O");
}

BOOST_AUTO_TEST_CASE(parse_multiple_rules_with_end_keyword) {
    std::istringstream input(R"(
        rule r1 A B
        require diff A B
        conclude diff B A
        end

        rule r2 X Y Z
        require coll X Y Z
        conclude coll Z Y X
        end
    )");

    std::vector<RuleSchema> rules = parse_rule_schemas(input);

    BOOST_REQUIRE_EQUAL(rules.size(), 2);

    BOOST_CHECK_EQUAL(rules.at(0).id, "r1");
    BOOST_CHECK_EQUAL(rules.at(1).id, "r2");

    BOOST_REQUIRE_EQUAL(rules.at(0).hypotheses.size(), 1);
    BOOST_REQUIRE_EQUAL(rules.at(0).conclusions.size(), 1);

    BOOST_CHECK_EQUAL(rules.at(0).hypotheses.at(0).name, "diff");
    BOOST_CHECK_EQUAL(rules.at(0).conclusions.at(0).name, "diff");

    BOOST_REQUIRE_EQUAL(rules.at(1).hypotheses.size(), 1);
    BOOST_REQUIRE_EQUAL(rules.at(1).conclusions.size(), 1);

    BOOST_CHECK_EQUAL(rules.at(1).hypotheses.at(0).name, "coll");
    BOOST_CHECK_EQUAL(rules.at(1).conclusions.at(0).name, "coll");
}

BOOST_AUTO_TEST_CASE(require_before_rule_is_error) {
    std::istringstream input(R"(
        require cong A B C D
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(conclude_before_rule_is_error) {
    std::istringstream input(R"(
        conclude cong A B C D
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(end_before_rule_is_error) {
    std::istringstream input(R"(
        end
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(rule_without_hypotheses_is_error) {
    std::istringstream input(R"(
        rule bad A B
        conclude diff A B
        end
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(rule_without_conclusions_is_error) {
    std::istringstream input(R"(
        rule bad A B
        require diff A B
        end
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(rule_without_end_is_error) {
    std::istringstream input(R"(
        rule bad A B
        require diff A B
        conclude diff B A
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(new_rule_before_end_is_error) {
    std::istringstream input(R"(
        rule r1 A B
        require diff A B
        conclude diff B A

        rule r2 X Y
        require diff X Y
        conclude diff Y X
        end
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(rule_with_duplicate_adjacent_variable_is_error) {
    std::istringstream input(R"(
        rule bad A A B
        require diff A B
        conclude diff B A
        end
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(rule_with_duplicate_non_adjacent_variable_is_error) {
    std::istringstream input(R"(
        rule bad A B C A
        require coll A B C
        conclude coll C B A
        end
    )");

    BOOST_CHECK_THROW(
        {
            const auto rules = parse_rule_schemas(input);
            (void)rules;
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_CASE(rule_with_unique_variables_is_valid) {
    std::istringstream input(R"(
        rule good A B C
        require coll A B C
        conclude coll C B A
        end
    )");

    const auto rules = parse_rule_schemas(input);

    BOOST_REQUIRE_EQUAL(rules.size(), 1);

    const RuleSchema &rule = rules.at(0);

    BOOST_CHECK_EQUAL(rule.id, "good");

    BOOST_REQUIRE_EQUAL(rule.variables.size(), 3);
    BOOST_CHECK_EQUAL(rule.variables.at(0), "A");
    BOOST_CHECK_EQUAL(rule.variables.at(1), "B");
    BOOST_CHECK_EQUAL(rule.variables.at(2), "C");
}

BOOST_AUTO_TEST_SUITE_END()
