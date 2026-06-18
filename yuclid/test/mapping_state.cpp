#define BOOST_TEST_MODULE mapping_state_test
#include <boost/test/unit_test.hpp>

#include <algorithm>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

#include "matchers/mapping_state.hpp"
#include "matchers/rule_schema.hpp"
#include "problem.hpp"
#include "type/point.hpp"

using namespace std;
using namespace Yuclid;

// ---- helpers -----------------------------------------------------------------
namespace {

    RulePredicatePattern pat(string name, vector<string> args) {
        return RulePredicatePattern{ .name = std::move(name), .args = std::move(args) };
    }

    // Build a schema with the given variables. MappingState only consumes
    // schema.variables (for sizing), so the predicate bodies are incidental.
    RuleSchema schema_with(vector<string> vars, vector<RulePredicatePattern> hyps) {
        vector<string> concl_args(vars.begin(),
                vars.begin() + std::min<size_t>(3, vars.size()));
        return RuleSchema{
            .id = "test_rule",
                .variables = vars,
                .hypotheses = std::move(hyps),
                .conclusions = { RulePredicatePattern{ .name = "coll", .args = concl_args } }
        };
    }

    // Canonical 4-variable schema (A,B,C,D) used by the assignment tests.
    RuleSchema abcd() {
        return schema_with({"A", "B", "C", "D"}, { pat("coll", {"A", "B", "C"}) });
    }

}  // namespace

// The problem must hold enough points for the indices the tests assign.
struct ProblemPointsFixture {
    ProblemPointsFixture() {
        problem::reset();
        for (int i = 0; i < 8; ++i) {
            problem::add_point("P" + to_string(i), static_cast<double>(i),
                    static_cast<double>(i * 2));
        }
    }
    ~ProblemPointsFixture() { problem::reset(); }
};

BOOST_FIXTURE_TEST_SUITE(mapping_state_suite, ProblemPointsFixture)

    // ===== commit 1: scaffolding, construction, 64-variable guard =================

    /**
     * @brief A freshly constructed state has nothing assigned and is not complete.
     */
    BOOST_AUTO_TEST_CASE(fresh_state_is_empty) {
        MappingState state(abcd(), problem::get_instance());

        BOOST_CHECK_EQUAL(state.assigned_count(), 0u);
        BOOST_CHECK(!state.is_complete());
        for (size_t v = 0; v < 4; ++v) {
            BOOST_CHECK(!state.is_assigned(v));
            BOOST_CHECK(!state.assigned_point_index(v).has_value());
        }
        for (size_t p = 0; p < 8; ++p) {
            BOOST_CHECK(!state.is_point_used(p));
        }
    }

/**
 * @brief The bitset-backed state rejects schemas with more than 64 variables.
 */
BOOST_AUTO_TEST_CASE(variable_count_ceiling_throws) {
    vector<string> many;
    for (int i = 0; i <= 64; ++i) {  // 65 variables, one over the limit
        many.push_back("V" + to_string(i));
    }
    RuleSchema big = schema_with(many, { pat("coll", {"V0", "V1", "V2"}) });

    BOOST_CHECK_THROW(MappingState(big, problem::get_instance()),
            std::invalid_argument);
}

/**
 * @brief Exactly 64 variables is still accepted.
 */
BOOST_AUTO_TEST_CASE(variable_count_at_limit_ok) {
    vector<string> sixtyfour;
    for (int i = 0; i < 64; ++i) {
        sixtyfour.push_back("V" + to_string(i));
    }
    RuleSchema schema = schema_with(sixtyfour, { pat("coll", {"V0", "V1", "V2"}) });

    BOOST_CHECK_NO_THROW(MappingState(schema, problem::get_instance()));
}

/**
 * @brief Applying a single assignment binds the variable and marks the point.
 */
BOOST_AUTO_TEST_CASE(apply_single_assignment) {
  MappingState state(abcd(), problem::get_instance());

  MappingExtension ext;
  ext.add_assignment(0, 3);  // A -> point 3
  BOOST_REQUIRE(state.apply_extension(ext));

  BOOST_CHECK(state.is_assigned(0));
  BOOST_REQUIRE(state.assigned_point_index(0).has_value());
  BOOST_CHECK_EQUAL(state.assigned_point_index(0).value(), 3u);
  BOOST_CHECK(state.is_point_used(3));
  BOOST_CHECK_EQUAL(state.assigned_count(), 1u);
  BOOST_CHECK(!state.is_assigned(1));
}

/**
 * @brief An extension binding several variables at once is applied atomically.
 */
BOOST_AUTO_TEST_CASE(apply_multiple_assignments) {
  MappingState state(abcd(), problem::get_instance());

  MappingExtension ext;
  ext.add_assignment(0, 1);  // A -> 1
  ext.add_assignment(1, 4);  // B -> 4
  BOOST_REQUIRE(state.apply_extension(ext));

  BOOST_CHECK_EQUAL(state.assigned_count(), 2u);
  BOOST_CHECK_EQUAL(state.assigned_point_index(0).value(), 1u);
  BOOST_CHECK_EQUAL(state.assigned_point_index(1).value(), 4u);
  BOOST_CHECK(state.is_point_used(1));
  BOOST_CHECK(state.is_point_used(4));
}

/**
 * @brief Injectivity: a point already used by one variable cannot be reused.
 */
BOOST_AUTO_TEST_CASE(injectivity_rejects_point_reuse) {
  MappingState state(abcd(), problem::get_instance());

  MappingExtension first;
  first.add_assignment(0, 3);  // A -> 3
  BOOST_REQUIRE(state.apply_extension(first));

  MappingExtension clash;
  clash.add_assignment(1, 3);  // B -> 3 (already taken)
  BOOST_CHECK(!state.apply_extension(clash));

  // State is unchanged by the rejected extension.
  BOOST_CHECK_EQUAL(state.assigned_count(), 1u);
  BOOST_CHECK(!state.is_assigned(1));
}

/**
 * @brief A repeated identical (var -> point) pair within one extension is fine.
 *
 * Providers for repeated-variable predicates (e.g. `cong A B A C`) emit the
 * shared variable twice; binding it to the same point must not be a conflict.
 */
BOOST_AUTO_TEST_CASE(repeated_identical_assignment_tolerated) {
  MappingState state(abcd(), problem::get_instance());

  MappingExtension ext;
  ext.add_assignment(0, 2);  // A -> 2
  ext.add_assignment(0, 2);  // A -> 2 again (same binding)
  BOOST_REQUIRE(state.apply_extension(ext));

  BOOST_CHECK_EQUAL(state.assigned_count(), 1u);
  BOOST_CHECK_EQUAL(state.assigned_point_index(0).value(), 2u);
}

BOOST_AUTO_TEST_SUITE_END()
