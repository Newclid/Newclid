#define BOOST_TEST_MODULE theorem_builder_test

#include <boost/test/unit_test.hpp>

#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include "problem.hpp"
#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "rules/theorem_builder.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/equal_angles.hpp"
#include "statement/midpoint.hpp"
#include "statement/para.hpp"
#include "statement/perp.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/statement.hpp"
#include "theorem.hpp"
#include "type/point.hpp"
#include "typedef.hpp"

using namespace Yuclid;

namespace {

    struct TheoremBuilderFixture {
        Problem problem;
        RuleMapping mapping;

        TheoremBuilderFixture() {
            mapping.emplace(
                "A",
                problem.add_point(
                    "A",
                    0.0,
                    0.0
                )
            );

            mapping.emplace(
                "B",
                problem.add_point(
                    "B",
                    1.0,
                    0.0
                )
            );

            mapping.emplace(
                "C",
                problem.add_point(
                    "C",
                    0.0,
                    1.0
                )
            );

            mapping.emplace(
                "D",
                problem.add_point(
                    "D",
                    1.0,
                    1.0
                )
            );

            mapping.emplace(
                "E",
                problem.add_point(
                    "E",
                    2.0,
                    0.0
                )
            );

            mapping.emplace(
                "F",
                problem.add_point(
                    "F",
                    2.0,
                    2.0
                )
            );
        }

        [[nodiscard]] const Point& point(
            const std::string& variable
        ) const {
            return mapping.at(variable);
        }

        void verify_point_order(
            const Statement& statement,
            const std::vector<std::string>& expected_variables
        ) const {
            const std::vector<Point> actual_points =
                statement.points();

            BOOST_REQUIRE_EQUAL(
                actual_points.size(),
                expected_variables.size()
            );

            for (std::size_t i = 0; i < expected_variables.size(); ++i) {
                BOOST_CHECK(
                    actual_points.at(i)
                    ==
                    point(expected_variables.at(i))
                );
            }
        }

        template <typename ExpectedStatementType>
        [[nodiscard]] const ExpectedStatementType& require_statement_type(
            const std::unique_ptr<Statement>& statement
        ) const {
            BOOST_REQUIRE(
                statement != nullptr
            );

            const ExpectedStatementType* typed_statement =
                dynamic_cast<const ExpectedStatementType*>(
                    statement.get()
                );

            BOOST_REQUIRE(
                typed_statement != nullptr
            );

            return *typed_statement;
        }
    };

    [[nodiscard]] RuleSchema make_schema(
        std::string id,
        std::vector<std::string> variables,
        std::vector<RulePredicatePattern> hypotheses,
        std::vector<RulePredicatePattern> conclusions
    ) {
        RuleSchema schema;
        schema.id = std::move(id);
        schema.variables = std::move(variables);
        schema.hypotheses = std::move(hypotheses);
        schema.conclusions = std::move(conclusions);
        return schema;
    }

}  // namespace

BOOST_FIXTURE_TEST_SUITE(
    theorem_builder_suite,
    TheoremBuilderFixture
)

/**
 * @brief RuleMapping resolves variables to the expected points.
 */
BOOST_AUTO_TEST_CASE(
    rule_mapping_resolves_variables_to_points
) {
    BOOST_CHECK_EQUAL(
        point("A").name(),
        "A"
    );

    BOOST_CHECK_EQUAL(
        point("B").name(),
        "B"
    );

    BOOST_CHECK_EQUAL(
        point("C").name(),
        "C"
    );

    BOOST_CHECK(
        point("A")
        !=
        point("B")
    );
}

/**
 * @brief Repeated variables in a pattern resolve to the same concrete point.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_preserves_repeated_variable_mapping
) {
    RuleSchema schema =
        make_schema(
            "repeated_variable_rule",
            {"A", "B"},
            {
                {
                    "cong",
                    {"A", "B", "A", "B"},
                },
            },
            {
                {
                    "coll",
                    {"A", "B", "A"},
                },
            }
        );

    const Theorem theorem =
        build_theorem_from_rule_schema(
            schema,
            mapping
        );

    BOOST_REQUIRE_EQUAL(
        theorem.hypotheses().size(),
        1U
    );

    BOOST_REQUIRE_EQUAL(
        theorem.conclusions().size(),
        1U
    );

    const DistEqDist& hypothesis =
        require_statement_type<DistEqDist>(
            theorem.hypotheses().at(0)
        );

    verify_point_order(
        hypothesis,
        {"A", "B", "A", "B"}
    );

    const Collinear& conclusion =
        require_statement_type<Collinear>(
            theorem.conclusions().at(0)
        );

    verify_point_order(
        conclusion,
        {"A", "B", "A"}
    );
}

/**
 * @brief TheoremBuilder assembles coll/cong hypotheses and para/perp
 * conclusions into the expected concrete statement types.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_builds_coll_cong_para_perp
) {
    RuleSchema schema =
        make_schema(
            "line_and_distance_rule",
            {"A", "B", "C", "D"},
            {
                {
                    "coll",
                    {"A", "B", "C"},
                },
                {
                    "cong",
                    {"A", "B", "C", "D"},
                },
            },
            {
                {
                    "para",
                    {"A", "B", "C", "D"},
                },
                {
                    "perp",
                    {"A", "C", "B", "D"},
                },
            }
        );

    const Theorem theorem =
        build_theorem_from_rule_schema(
            schema,
            mapping
        );

    BOOST_REQUIRE_EQUAL(
        theorem.hypotheses().size(),
        2U
    );

    BOOST_REQUIRE_EQUAL(
        theorem.conclusions().size(),
        2U
    );

    const Collinear& collinear =
        require_statement_type<Collinear>(
            theorem.hypotheses().at(0)
        );

    verify_point_order(
        collinear,
        {"A", "B", "C"}
    );

    const DistEqDist& congruent =
        require_statement_type<DistEqDist>(
            theorem.hypotheses().at(1)
        );

    verify_point_order(
        congruent,
        {"A", "B", "C", "D"}
    );

    const Parallel& parallel =
        require_statement_type<Parallel>(
            theorem.conclusions().at(0)
        );

    verify_point_order(
        parallel,
        {"A", "B", "C", "D"}
    );

    const Perpendicular& perpendicular =
        require_statement_type<Perpendicular>(
            theorem.conclusions().at(1)
        );

    verify_point_order(
        perpendicular,
        {"A", "C", "B", "D"}
    );
}

/**
 * @brief TheoremBuilder preserves the order-sensitive midpoint mapping and
 * builds angle-equality conclusions.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_builds_midpoint_and_eqangle
) {
    RuleSchema schema =
        make_schema(
            "midpoint_angle_rule",
            {"A", "B", "C", "D", "E", "F"},
            {
                {
                    "midp",
                    {"A", "B", "C"},
                },
            },
            {
                {
                    "eqangle",
                    {"A", "B", "C", "D", "E", "F"},
                },
            }
        );

    const Theorem theorem =
        build_theorem_from_rule_schema(
            schema,
            mapping
        );

    BOOST_REQUIRE_EQUAL(
        theorem.hypotheses().size(),
        1U
    );

    BOOST_REQUIRE_EQUAL(
        theorem.conclusions().size(),
        1U
    );

    const Midpoint& midpoint =
        require_statement_type<Midpoint>(
            theorem.hypotheses().at(0)
        );

    /*
     * The custom-rule spelling is midp A B C, meaning B is the midpoint
     * of AC. The concrete Midpoint statement stores the midpoint first,
     * followed by the two segment endpoints.
     */
    verify_point_order(
        midpoint,
        {"B", "A", "C"}
    );

    const EqualAngles& equal_angles =
        require_statement_type<EqualAngles>(
            theorem.conclusions().at(0)
        );

    verify_point_order(
        equal_angles,
        {"A", "B", "C", "D", "E", "F"}
    );
}

/**
 * @brief TheoremBuilder builds constant predicates through StatementBuilder
 * and preserves their parsed constant value.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_builds_constant_predicate
) {
    RuleSchema schema =
        make_schema(
            "constant_ratio_rule",
            {"A", "B", "C", "D"},
            {
                {
                    "rconst",
                    {"A", "B", "C", "D", "5/2"},
                },
            },
            {
                {
                    "cong",
                    {"A", "B", "C", "D"},
                },
            }
        );

    const Theorem theorem =
        build_theorem_from_rule_schema(
            schema,
            mapping
        );

    BOOST_REQUIRE_EQUAL(
        theorem.hypotheses().size(),
        1U
    );

    BOOST_REQUIRE_EQUAL(
        theorem.conclusions().size(),
        1U
    );

    const RatioDistEquals& ratio_statement =
        require_statement_type<RatioDistEquals>(
            theorem.hypotheses().at(0)
        );

    verify_point_order(
        ratio_statement,
        {"A", "B", "C", "D"}
    );

    BOOST_CHECK(
        ratio_statement.ratio()
        ==
        NNRat(5, 2)
    );

    const DistEqDist& congruent =
        require_statement_type<DistEqDist>(
            theorem.conclusions().at(0)
        );

    verify_point_order(
        congruent,
        {"A", "B", "C", "D"}
    );
}

/**
 * @brief TheoremBuilder supports patterns that expand into multiple concrete
 * statements.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_expands_rolling_patterns
) {
    RuleSchema schema =
        make_schema(
            "rolling_coll_rule",
            {"A", "B", "C", "D", "E"},
            {
                {
                    "coll",
                    {"A", "B", "C", "D", "E"},
                },
            },
            {
                {
                    "coll",
                    {"E", "D", "C"},
                },
            }
        );

    const Theorem theorem =
        build_theorem_from_rule_schema(
            schema,
            mapping
        );

    /*
     * coll A B C D E expands to:
     * - coll A B C
     * - coll B C D
     * - coll C D E
     */
    BOOST_REQUIRE_EQUAL(
        theorem.hypotheses().size(),
        3U
    );

    BOOST_REQUIRE_EQUAL(
        theorem.conclusions().size(),
        1U
    );

    const Collinear& first_hypothesis =
        require_statement_type<Collinear>(
            theorem.hypotheses().at(0)
        );

    verify_point_order(
        first_hypothesis,
        {"A", "B", "C"}
    );

    const Collinear& second_hypothesis =
        require_statement_type<Collinear>(
            theorem.hypotheses().at(1)
        );

    verify_point_order(
        second_hypothesis,
        {"B", "C", "D"}
    );

    const Collinear& third_hypothesis =
        require_statement_type<Collinear>(
            theorem.hypotheses().at(2)
        );

    verify_point_order(
        third_hypothesis,
        {"C", "D", "E"}
    );

    const Collinear& conclusion =
        require_statement_type<Collinear>(
            theorem.conclusions().at(0)
        );

    verify_point_order(
        conclusion,
        {"E", "D", "C"}
    );
}

/**
 * @brief Theorem name, Newclid rule ID, and max point are copied from the
 * schema/mapped statements correctly.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_sets_metadata_and_max_point
) {
    RuleSchema schema =
        make_schema(
            "custom_metadata_rule",
            {"A", "B", "C", "F"},
            {
                {
                    "coll",
                    {"A", "B", "C"},
                },
            },
            {
                {
                    "para",
                    {"A", "B", "C", "F"},
                },
            }
        );

    const char* schema_id_data =
        schema.id.data();

    const std::size_t schema_id_size =
        schema.id.size();

    const Theorem theorem =
        build_theorem_from_rule_schema(
            schema,
            mapping
        );

    BOOST_CHECK_EQUAL(
        std::string(theorem.name()),
        schema.id
    );

    BOOST_CHECK_EQUAL(
        std::string(theorem.newclid_rule()),
        schema.id
    );

    /*
     * Theorem stores name/newclid_rule as string_view. These checks lock in
     * that TheoremBuilder passes schema.id directly instead of a temporary.
     */
    BOOST_CHECK(
        theorem.name().data()
        ==
        schema_id_data
    );

    BOOST_CHECK(
        theorem.newclid_rule().data()
        ==
        schema_id_data
    );

    BOOST_CHECK_EQUAL(
        theorem.name().size(),
        schema_id_size
    );

    BOOST_CHECK_EQUAL(
        theorem.newclid_rule().size(),
        schema_id_size
    );

    BOOST_CHECK(
        theorem.max_point()
        ==
        point("F")
    );
}

/**
 * @brief Building a theorem fails when a required schema variable is missing
 * from the concrete mapping.
 */
BOOST_AUTO_TEST_CASE(
    theorem_builder_throws_for_missing_mapping_variable
) {
    RuleSchema schema =
        make_schema(
            "missing_variable_rule",
            {"A", "B", "Z"},
            {
                {
                    "coll",
                    {"A", "B", "Z"},
                },
            },
            {
                {
                    "cong",
                    {"A", "B", "A", "B"},
                },
            }
        );

    BOOST_CHECK_THROW(
        {
            const Theorem theorem =
                build_theorem_from_rule_schema(
                    schema,
                    mapping
                );

            static_cast<void>(
                theorem
            );
        },
        std::runtime_error
    );
}

BOOST_AUTO_TEST_SUITE_END()
