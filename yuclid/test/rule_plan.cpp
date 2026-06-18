#define BOOST_TEST_MODULE rule_plan_test

#include <boost/test/unit_test.hpp>

#include <cstddef>
#include <string>
#include <utility>
#include <vector>

#include "matchers/rule_plan.hpp"
#include "rules/rule_schema.hpp"

using namespace Yuclid;

namespace {

    RulePredicatePattern pattern(
        std::string name,
        std::vector<std::string> arguments
    ) {
        return RulePredicatePattern{
            .name = std::move(name),
            .args = std::move(arguments),
        };
    }

    RuleSchema make_schema(
        std::vector<std::string> variables,
        std::vector<RulePredicatePattern> hypotheses,
        std::vector<RulePredicatePattern> conclusions
    ) {
        return RuleSchema{
            .id = "test_rule",
            .variables = std::move(variables),
            .hypotheses = std::move(hypotheses),
            .conclusions = std::move(conclusions),
        };
    }

    const PlannedPredicate* find_predicate(
        const std::vector<PlannedPredicate>& predicates,
        const std::string& name
    ) {
        for (const PlannedPredicate& predicate : predicates) {
            if (predicate.pattern.name == name) {
                return &predicate;
            }
        }

        return nullptr;
    }

    bool contains_predicate(
        const std::vector<PlannedPredicate>& predicates,
        const std::string& name
    ) {
        return find_predicate(predicates, name) != nullptr;
    }

}  // namespace

BOOST_AUTO_TEST_SUITE(rule_plan_suite)

/**
 * The generated plan keeps a pointer to the source schema.
 */
BOOST_AUTO_TEST_CASE(plan_references_source_schema) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern("coll", {"A", "B", "C"}),
        },
        {
            pattern("cong", {"A", "B", "A", "C"}),
        }
    );

    RulePlan plan = build_rule_plan(rule_schema);

    BOOST_CHECK_EQUAL(plan.schema, &rule_schema);
    BOOST_CHECK_EQUAL(plan.schema->id, "test_rule");
}

/**
 * Candidate-generator predicates are placed in the generator collection.
 */
BOOST_AUTO_TEST_CASE(generator_predicates_are_classified) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern("coll", {"A", "B", "C"}),
        },
        {
            pattern("cong", {"A", "B", "A", "C"}),
        }
    );

    RulePlan plan = build_rule_plan(rule_schema);

    BOOST_CHECK(
        contains_predicate(
            plan.candidate_generators,
            "coll"
        )
    );
    BOOST_CHECK(
        contains_predicate(
            plan.candidate_generators,
            "cong"
        )
    );

    BOOST_CHECK(
        !contains_predicate(
            plan.validators,
            "coll"
        )
    );
    BOOST_CHECK(
        !contains_predicate(
            plan.unsupported_predicates,
            "coll"
        )
    );
}

/**
 * Predicates absent from the metadata table are marked unsupported.
 */
BOOST_AUTO_TEST_CASE(unknown_predicate_is_marked_unsupported) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern("ncoll", {"A", "B", "C"}),
        },
        {
            pattern("coll", {"A", "B", "C"}),
        }
    );

    RulePlan plan = build_rule_plan(rule_schema);

    BOOST_CHECK(
        contains_predicate(
            plan.unsupported_predicates,
            "ncoll"
        )
    );
    BOOST_CHECK(
        !contains_predicate(
            plan.candidate_generators,
            "ncoll"
        )
    );
    BOOST_CHECK(
        !contains_predicate(
            plan.candidate_filters,
            "ncoll"
        )
    );
    BOOST_CHECK(
        !contains_predicate(
            plan.validators,
            "ncoll"
        )
    );
}

/**
 * Supported predicates without a generator are planned as validators.
 */
BOOST_AUTO_TEST_CASE(
    supported_non_generator_is_planned_as_validator
) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C", "D"},
        {
            pattern("midp", {"A", "B", "C"}),
        },
        {
            pattern("coll", {"A", "B", "D"}),
        }
    );

    RulePlan plan = build_rule_plan(rule_schema);

    BOOST_CHECK(
        contains_predicate(
            plan.validators,
            "midp"
        )
    );
    BOOST_CHECK(
        !contains_predicate(
            plan.candidate_generators,
            "midp"
        )
    );
    BOOST_CHECK(
        !contains_predicate(
            plan.unsupported_predicates,
            "midp"
        )
    );
}

/**
 * Variable indices use the positions from the schema declaration.
 */
BOOST_AUTO_TEST_CASE(variable_indices_match_schema_indices) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern("coll", {"A", "B", "C"}),
        },
        {}
    );

    RulePlan plan = build_rule_plan(rule_schema);

    const PlannedPredicate* predicate =
        find_predicate(
            plan.candidate_generators,
            "coll"
        );

    BOOST_REQUIRE(predicate != nullptr);
    BOOST_REQUIRE_EQUAL(
        predicate->variable_indices.size(),
        3U
    );

    BOOST_CHECK_EQUAL(
        predicate->variable_indices[0],
        0U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[1],
        1U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[2],
        2U
    );
}

/**
 * Indices are stored in the order in which variables first occur in the
 * predicate pattern.
 */
BOOST_AUTO_TEST_CASE(
    variable_indices_follow_pattern_order
) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern("coll", {"C", "A", "B"}),
        },
        {}
    );

    RulePlan plan = build_rule_plan(rule_schema);

    const PlannedPredicate* predicate =
        find_predicate(
            plan.candidate_generators,
            "coll"
        );

    BOOST_REQUIRE(predicate != nullptr);
    BOOST_REQUIRE_EQUAL(
        predicate->variable_indices.size(),
        3U
    );

    BOOST_CHECK_EQUAL(
        predicate->variable_indices[0],
        2U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[1],
        0U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[2],
        1U
    );
}

/**
 * A repeated variable is included only once, at its first occurrence.
 */
BOOST_AUTO_TEST_CASE(
    repeated_variable_index_is_deduplicated
) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern(
                "cong",
                {"A", "B", "A", "C"}
            ),
        },
        {}
    );

    RulePlan plan = build_rule_plan(rule_schema);

    const PlannedPredicate* predicate =
        find_predicate(
            plan.candidate_generators,
            "cong"
        );

    BOOST_REQUIRE(predicate != nullptr);
    BOOST_REQUIRE_EQUAL(
        predicate->variable_indices.size(),
        3U
    );

    BOOST_CHECK_EQUAL(
        predicate->variable_indices[0],
        0U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[1],
        1U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[2],
        2U
    );
}

/**
 * Constant arguments remain in the predicate pattern but are excluded from
 * its variable-index list.
 */
BOOST_AUTO_TEST_CASE(
    constant_arguments_are_excluded_from_variable_indices
) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C", "D"},
        {
            pattern(
                "rconst",
                {"A", "B", "C", "D", "1/2"}
            ),
        },
        {}
    );

    RulePlan plan = build_rule_plan(rule_schema);

    const PlannedPredicate* predicate =
        find_predicate(
            plan.validators,
            "rconst"
        );

    BOOST_REQUIRE(predicate != nullptr);
    BOOST_REQUIRE_EQUAL(
        predicate->variable_indices.size(),
        4U
    );

    BOOST_CHECK_EQUAL(
        predicate->variable_indices[0],
        0U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[1],
        1U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[2],
        2U
    );
    BOOST_CHECK_EQUAL(
        predicate->variable_indices[3],
        3U
    );

    BOOST_REQUIRE_EQUAL(
        predicate->pattern.args.size(),
        5U
    );
    BOOST_CHECK_EQUAL(
        predicate->pattern.args.back(),
        "1/2"
    );
}

/**
 * Every hypothesis and conclusion is classified into one plan collection.
 */
BOOST_AUTO_TEST_CASE(every_predicate_is_classified_once) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C", "D"},
        {
            pattern("coll", {"A", "B", "C"}),
            pattern("ncoll", {"A", "B", "D"}),
            pattern("midp", {"A", "C", "D"}),
        },
        {
            pattern("cong", {"A", "B", "C", "D"}),
        }
    );

    RulePlan plan = build_rule_plan(rule_schema);

    const std::size_t classified_count =
        plan.candidate_generators.size()
        + plan.candidate_filters.size()
        + plan.validators.size()
        + plan.unsupported_predicates.size();

    const std::size_t predicate_count =
        rule_schema.hypotheses.size()
        + rule_schema.conclusions.size();

    BOOST_CHECK_EQUAL(
        classified_count,
        predicate_count
    );

    BOOST_CHECK_EQUAL(
        plan.candidate_generators.size(),
        2U
    );
    BOOST_CHECK_EQUAL(
        plan.validators.size(),
        1U
    );
    BOOST_CHECK_EQUAL(
        plan.unsupported_predicates.size(),
        1U
    );
}

/**
 * Metadata is copied into the planned predicate.
 */
BOOST_AUTO_TEST_CASE(
    planned_predicate_contains_matching_metadata
) {
    RuleSchema rule_schema = make_schema(
        {"A", "B", "C"},
        {
            pattern("coll", {"A", "B", "C"}),
        },
        {}
    );

    RulePlan plan = build_rule_plan(rule_schema);

    const PlannedPredicate* predicate =
        find_predicate(
            plan.candidate_generators,
            "coll"
        );

    BOOST_REQUIRE(predicate != nullptr);

    BOOST_CHECK(
        predicate->metadata.role
        == PredicateMatchingRole::CandidateGenerator
    );
    BOOST_CHECK_EQUAL(
        predicate->metadata.base_cost,
        10
    );
    BOOST_CHECK_GT(
        predicate->metadata.base_cost,
        0
    );
}

/**
 * Multiple schemas produce plans in the same order and retain references to
 * their respective source schemas.
 */
BOOST_AUTO_TEST_CASE(build_rule_plans_preserves_schema_order) {
    std::vector<RuleSchema> schemas;

    schemas.push_back(
        make_schema(
            {"A", "B", "C"},
            {
                pattern("coll", {"A", "B", "C"}),
            },
            {}
        )
    );

    schemas.push_back(
        make_schema(
            {"P", "Q", "R", "S"},
            {
                pattern("cong", {"P", "Q", "R", "S"}),
            },
            {}
        )
    );

    const std::vector<RulePlan> plans =
        build_rule_plans(schemas);

    BOOST_REQUIRE_EQUAL(plans.size(), 2U);

    BOOST_CHECK_EQUAL(
        plans[0].schema,
        &schemas[0]
    );
    BOOST_CHECK_EQUAL(
        plans[1].schema,
        &schemas[1]
    );

    BOOST_CHECK(
        contains_predicate(
            plans[0].candidate_generators,
            "coll"
        )
    );
    BOOST_CHECK(
        contains_predicate(
            plans[1].candidate_generators,
            "cong"
        )
    );
}

BOOST_AUTO_TEST_SUITE_END()
