#define BOOST_TEST_MODULE mapping_state_test

#include <boost/test/unit_test.hpp>

#include <algorithm>
#include <cstddef>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "matchers/mapping_state.hpp"
#include "problem.hpp"
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

    /**
     * Build a schema with the given variables.
     *
     * MappingState uses the variables for its indexed assignment storage.
     * The hypothesis and conclusion are incidental for these tests.
     */
    RuleSchema schema_with(
        std::vector<std::string> variables,
        std::vector<RulePredicatePattern> hypotheses
    ) {
        std::vector<std::string> conclusion_arguments(
            variables.begin(),
            variables.begin()
                + std::min<std::size_t>(3, variables.size())
        );

        return RuleSchema{
            .id = "test_rule",
            .variables = std::move(variables),
            .hypotheses = std::move(hypotheses),
            .conclusions = {
                RulePredicatePattern{
                    .name = "coll",
                    .args = std::move(conclusion_arguments),
                },
            },
        };
    }

    RuleSchema abcd_schema() {
        return schema_with(
            {"A", "B", "C", "D"},
            {
                pattern(
                    "coll",
                    {"A", "B", "C"}
                ),
            }
        );
    }

}  // namespace

struct MappingStateFixture {
    Problem problem;
    RuleSchema schema;

    MappingStateFixture()
        : schema(abcd_schema())
    {
        for (int index = 0; index < 8; ++index) {
            static_cast<void>(
                problem.add_point(
                    "P" + std::to_string(index),
                    static_cast<double>(index),
                    static_cast<double>(index * 2)
                )
            );
        }
    }
};

BOOST_FIXTURE_TEST_SUITE(
    mapping_state_suite,
    MappingStateFixture
)

/**
 * A new extension contains no assignments and can be cleared for reuse.
 */
BOOST_AUTO_TEST_CASE(mapping_extension_tracks_and_clears_assignments) {
    MappingExtension extension;

    BOOST_CHECK(extension.empty());
    BOOST_CHECK(extension.assignments().empty());

    extension.add_assignment(0, 2);
    extension.add_assignment(1, 4);

    BOOST_CHECK(!extension.empty());
    BOOST_REQUIRE_EQUAL(
        extension.assignments().size(),
        2U
    );

    BOOST_CHECK_EQUAL(
        extension.assignments()[0].variable_idx,
        0U
    );
    BOOST_CHECK_EQUAL(
        extension.assignments()[0].point_idx,
        2U
    );
    BOOST_CHECK_EQUAL(
        extension.assignments()[1].variable_idx,
        1U
    );
    BOOST_CHECK_EQUAL(
        extension.assignments()[1].point_idx,
        4U
    );

    extension.clear_assignments();

    BOOST_CHECK(extension.empty());
    BOOST_CHECK(extension.assignments().empty());
}

/**
 * A freshly constructed state has nothing assigned and is incomplete.
 */
BOOST_AUTO_TEST_CASE(fresh_state_is_empty) {
    MappingState state(schema, problem);

    BOOST_CHECK_EQUAL(state.assigned_count(), 0U);
    BOOST_CHECK(!state.is_complete());

    for (
        std::size_t variable_index = 0;
        variable_index < schema.variables.size();
        ++variable_index
    ) {
        BOOST_CHECK(
            state.is_rule_variable(variable_index)
        );
        BOOST_CHECK(
            !state.is_assigned(variable_index)
        );
        BOOST_CHECK(
            !state.assigned_point_index(
                variable_index
            ).has_value()
        );
    }

    BOOST_CHECK(
        !state.is_rule_variable(
            schema.variables.size()
        )
    );

    for (
        std::size_t point_index = 0;
        point_index < problem.num_points();
        ++point_index
    ) {
        BOOST_CHECK(
            !state.is_point_used(point_index)
        );
    }

    const std::vector<RuleVariableIndex> unassigned =
        state.unassigned_variables();

    BOOST_REQUIRE_EQUAL(unassigned.size(), 4U);
    BOOST_CHECK_EQUAL(unassigned[0], 0U);
    BOOST_CHECK_EQUAL(unassigned[1], 1U);
    BOOST_CHECK_EQUAL(unassigned[2], 2U);
    BOOST_CHECK_EQUAL(unassigned[3], 3U);
}

/**
 * MappingState uses a 64-bit variable mask and rejects larger schemas.
 */
BOOST_AUTO_TEST_CASE(variable_count_ceiling_throws) {
    std::vector<std::string> variables;

    for (int index = 0; index < 65; ++index) {
        variables.push_back(
            "V" + std::to_string(index)
        );
    }

    RuleSchema large_schema = schema_with(
        std::move(variables),
        {
            pattern(
                "coll",
                {"V0", "V1", "V2"}
            ),
        }
    );

    BOOST_CHECK_THROW(
        (void)MappingState(
            large_schema,
            problem
        ),
        std::invalid_argument
    );
}

/**
 * Exactly 64 variables is still supported.
 */
BOOST_AUTO_TEST_CASE(variable_count_at_limit_is_accepted) {
    std::vector<std::string> variables;

    for (int index = 0; index < 64; ++index) {
        variables.push_back(
            "V" + std::to_string(index)
        );
    }

    RuleSchema limit_schema = schema_with(
        std::move(variables),
        {
            pattern(
                "coll",
                {"V0", "V1", "V2"}
            ),
        }
    );

    BOOST_CHECK_NO_THROW(
        (void)MappingState(
            limit_schema,
            problem
        )
    );
}

/**
 * Applying one assignment binds the variable and marks the point as used.
 */
BOOST_AUTO_TEST_CASE(try_apply_single_assignment) {
    MappingState state(schema, problem);

    MappingExtension extension;
    extension.add_assignment(0, 3);

    BOOST_REQUIRE(
        state.try_apply_extension(extension)
    );

    BOOST_CHECK(state.is_assigned(0));

    const std::optional<ProblemPointIndex> assigned_point =
        state.assigned_point_index(0);

    BOOST_REQUIRE(assigned_point.has_value());
    BOOST_CHECK_EQUAL(*assigned_point, 3U);

    BOOST_CHECK(state.is_point_used(3));
    BOOST_CHECK_EQUAL(state.assigned_count(), 1U);
    BOOST_CHECK(!state.is_complete());
    BOOST_CHECK(!state.is_assigned(1));
}

/**
 * The Point overload converts the point to its problem index.
 */
BOOST_AUTO_TEST_CASE(try_apply_point_assignment) {
    MappingState state(schema, problem);

    const Point point = problem.point_at(5);

    BOOST_REQUIRE(
        state.try_apply_assignment(0, point)
    );

    BOOST_REQUIRE(
        state.assigned_point_index(0).has_value()
    );

    BOOST_CHECK_EQUAL(
        *state.assigned_point_index(0),
        5U
    );
    BOOST_CHECK(state.is_point_used(point));
}

/**
 * Several compatible assignments can be applied in one extension.
 */
BOOST_AUTO_TEST_CASE(try_apply_multiple_assignments) {
    MappingState state(schema, problem);

    MappingExtension extension;
    extension.add_assignment(0, 1);
    extension.add_assignment(1, 4);

    BOOST_REQUIRE(
        state.try_apply_extension(extension)
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 2U);

    BOOST_REQUIRE(
        state.assigned_point_index(0).has_value()
    );
    BOOST_REQUIRE(
        state.assigned_point_index(1).has_value()
    );

    BOOST_CHECK_EQUAL(
        *state.assigned_point_index(0),
        1U
    );
    BOOST_CHECK_EQUAL(
        *state.assigned_point_index(1),
        4U
    );

    BOOST_CHECK(state.is_point_used(1));
    BOOST_CHECK(state.is_point_used(4));

    const std::vector<RuleVariableIndex> unassigned =
        state.unassigned_variables();

    BOOST_REQUIRE_EQUAL(unassigned.size(), 2U);
    BOOST_CHECK_EQUAL(unassigned[0], 2U);
    BOOST_CHECK_EQUAL(unassigned[1], 3U);
}

/**
 * Different variables cannot use the same problem point.
 */
BOOST_AUTO_TEST_CASE(injectivity_rejects_point_reuse) {
    MappingState state(schema, problem);

    MappingExtension first_extension;
    first_extension.add_assignment(0, 3);

    BOOST_REQUIRE(
        state.try_apply_extension(first_extension)
    );

    MappingExtension conflicting_extension;
    conflicting_extension.add_assignment(1, 3);

    BOOST_CHECK(
        !state.try_apply_extension(
            conflicting_extension
        )
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 1U);
    BOOST_CHECK(state.is_assigned(0));
    BOOST_CHECK(!state.is_assigned(1));
    BOOST_CHECK(state.is_point_used(3));
}

/**
 * If one assignment in an extension fails, earlier assignments from that same
 * extension are rolled back.
 */
BOOST_AUTO_TEST_CASE(
    failed_extension_rolls_back_partial_assignments
) {
    MappingState state(schema, problem);

    MappingExtension extension;
    extension.add_assignment(0, 2);
    extension.add_assignment(1, 2);

    BOOST_CHECK(
        !state.try_apply_extension(extension)
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 0U);
    BOOST_CHECK(!state.is_assigned(0));
    BOOST_CHECK(!state.is_assigned(1));
    BOOST_CHECK(!state.is_point_used(2));
}

/**
 * Applying the same variable-to-point assignment more than once is valid.
 *
 * This may occur when a provider handles a predicate containing a repeated
 * variable, such as `cong A B A C`.
 */
BOOST_AUTO_TEST_CASE(
    repeated_identical_assignment_is_accepted
) {
    MappingState state(schema, problem);

    MappingExtension extension;
    extension.add_assignment(0, 2);
    extension.add_assignment(0, 2);

    BOOST_REQUIRE(
        state.try_apply_extension(extension)
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 1U);

    BOOST_REQUIRE(
        state.assigned_point_index(0).has_value()
    );

    BOOST_CHECK_EQUAL(
        *state.assigned_point_index(0),
        2U
    );
}

/**
 * The same variable cannot be assigned to two different points.
 */
BOOST_AUTO_TEST_CASE(
    repeated_conflicting_assignment_is_rejected
) {
    MappingState state(schema, problem);

    MappingExtension extension;
    extension.add_assignment(0, 2);
    extension.add_assignment(0, 3);

    BOOST_CHECK(
        !state.try_apply_extension(extension)
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 0U);
    BOOST_CHECK(!state.is_assigned(0));
    BOOST_CHECK(!state.is_point_used(2));
    BOOST_CHECK(!state.is_point_used(3));
}

/**
 * Out-of-range variable and point indices are rejected without mutation.
 */
BOOST_AUTO_TEST_CASE(
    invalid_assignment_indices_are_rejected
) {
    MappingState state(schema, problem);

    BOOST_CHECK(
        !state.try_apply_assignment(
            schema.variables.size(),
            0
        )
    );

    BOOST_CHECK(
        !state.try_apply_assignment(
            0,
            problem.num_points()
        )
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 0U);
    BOOST_CHECK(!state.is_complete());
    BOOST_CHECK(!state.is_assigned(0));
}

/**
 * Rolling back restores the state captured before deeper assignments.
 */
BOOST_AUTO_TEST_CASE(rollback_restores_partial_state) {
    MappingState state(schema, problem);

    MappingExtension base_extension;
    base_extension.add_assignment(0, 3);

    BOOST_REQUIRE(
        state.try_apply_extension(base_extension)
    );

    const MappingStateSnapshot snapshot =
        state.snapshot();

    MappingExtension deeper_extension;
    deeper_extension.add_assignment(1, 4);

    BOOST_REQUIRE(
        state.try_apply_extension(deeper_extension)
    );

    BOOST_CHECK_EQUAL(state.assigned_count(), 2U);

    state.rollback(snapshot);

    BOOST_CHECK_EQUAL(state.assigned_count(), 1U);
    BOOST_CHECK(state.is_assigned(0));
    BOOST_CHECK(!state.is_assigned(1));
    BOOST_CHECK(state.is_point_used(3));
    BOOST_CHECK(!state.is_point_used(4));
}

/**
 * Rolling back to an empty snapshot removes every assignment.
 */
BOOST_AUTO_TEST_CASE(rollback_to_empty_state) {
    MappingState state(schema, problem);

    const MappingStateSnapshot empty_snapshot =
        state.snapshot();

    MappingExtension extension;
    extension.add_assignment(0, 1);
    extension.add_assignment(1, 2);

    BOOST_REQUIRE(
        state.try_apply_extension(extension)
    );

    state.rollback(empty_snapshot);

    BOOST_CHECK_EQUAL(state.assigned_count(), 0U);
    BOOST_CHECK(!state.is_assigned(0));
    BOOST_CHECK(!state.is_assigned(1));
    BOOST_CHECK(!state.is_point_used(1));
    BOOST_CHECK(!state.is_point_used(2));
}

/**
 * An incomplete state cannot be converted to a complete RuleMapping.
 */
BOOST_AUTO_TEST_CASE(
    incomplete_state_returns_no_complete_mapping
) {
    MappingState state(schema, problem);

    BOOST_CHECK(
        !state.to_rule_mapping().has_value()
    );

    BOOST_REQUIRE(
        state.try_apply_assignment(0, 3)
    );

    BOOST_CHECK(
        !state.to_rule_mapping().has_value()
    );

    const RuleMapping partial_mapping =
        state.to_partial_rule_mapping();

    BOOST_CHECK_EQUAL(partial_mapping.size(), 1U);
    BOOST_CHECK_EQUAL(
        partial_mapping.at("A").get(),
        3U
    );
    BOOST_CHECK(
        partial_mapping.find("B")
            == partial_mapping.end()
    );
}

/**
 * A complete state converts every schema variable to the expected point.
 */
BOOST_AUTO_TEST_CASE(
    complete_state_converts_to_rule_mapping
) {
    MappingState state(schema, problem);

    MappingExtension extension;
    extension.add_assignment(0, 0);
    extension.add_assignment(1, 1);
    extension.add_assignment(2, 2);
    extension.add_assignment(3, 3);

    BOOST_REQUIRE(
        state.try_apply_extension(extension)
    );

    BOOST_CHECK(state.is_complete());
    BOOST_CHECK_EQUAL(state.assigned_count(), 4U);
    BOOST_CHECK(state.unassigned_variables().empty());

    const std::optional<RuleMapping> complete_mapping =
        state.to_rule_mapping();

    BOOST_REQUIRE(complete_mapping.has_value());
    BOOST_CHECK_EQUAL(complete_mapping->size(), 4U);

    BOOST_CHECK_EQUAL(
        complete_mapping->at("A").get(),
        0U
    );
    BOOST_CHECK_EQUAL(
        complete_mapping->at("B").get(),
        1U
    );
    BOOST_CHECK_EQUAL(
        complete_mapping->at("C").get(),
        2U
    );
    BOOST_CHECK_EQUAL(
        complete_mapping->at("D").get(),
        3U
    );

    const RuleMapping partial_mapping =
        state.to_partial_rule_mapping();

    BOOST_CHECK_EQUAL(partial_mapping.size(), 4U);
}

BOOST_AUTO_TEST_SUITE_END()
