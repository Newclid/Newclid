#define BOOST_TEST_MODULE rule_plan_test
#include <boost/test/unit_test.hpp>

#include <string>
#include <vector>

#include "matchers/rule_plan.hpp"
#include "matchers/rule_schema.hpp"

using namespace std;
using namespace Yuclid;

// ---- helpers -----------------------------------------------------------------
namespace {

    RulePredicatePattern pat(string name, vector<string> args) {
        return RulePredicatePattern{ .name = std::move(name), .args = std::move(args) };
    }

    RuleSchema schema(vector<string> vars,
            vector<RulePredicatePattern> hyps,
            vector<RulePredicatePattern> concls) {
        return RuleSchema{
            .id = "test_rule",
            .variables = std::move(vars),
            .hypotheses = std::move(hyps),
            .conclusions = std::move(concls)
        };
    }

    const PlannedPredicate* find_pred(const vector<PlannedPredicate>& v,
            const string& name) {
        for (const auto& p : v) {
            if (p.pattern.name == name) {
                return &p;
            }
        }
        return nullptr;
    }

    bool contains_pred(const vector<PlannedPredicate>& v, const string& name) {
        return find_pred(v, name) != nullptr;
    }

}  // namespace

BOOST_AUTO_TEST_SUITE(rule_plan_suite)

    /**
     * @brief coll/cong predicates are classified as candidate generators.
     */
    BOOST_AUTO_TEST_CASE(generator_predicates_classified) {
        RulePlan plan = build_rule_plan(
                schema({"A", "B", "C"},
                    { pat("coll", {"A", "B", "C"}) },
                    { pat("cong", {"A", "B", "A", "C"}) }));

        BOOST_CHECK(contains_pred(plan.candidate_generators, "coll"));
        BOOST_CHECK(contains_pred(plan.candidate_generators, "cong"));
        BOOST_CHECK(!contains_pred(plan.unsupported_predicates, "coll"));
    }

/**
 * @brief Predicates absent from the metadata table land in unsupported_predicates.
 */
BOOST_AUTO_TEST_CASE(unsupported_predicate_flagged) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C"},
                { pat("ncoll", {"A", "B", "C"}) },
                { pat("coll", {"A", "B", "C"}) }));

    BOOST_CHECK(contains_pred(plan.unsupported_predicates, "ncoll"));
    BOOST_CHECK(!contains_pred(plan.candidate_generators, "ncoll"));
    BOOST_CHECK(!contains_pred(plan.validators, "ncoll"));
}

/**
 * @brief A supported non-generator predicate is planned, not dropped.
 */
BOOST_AUTO_TEST_CASE(supported_non_generator_is_planned) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C", "D"},
                { pat("midp", {"A", "B", "C"}) },
                { pat("coll", {"A", "B", "D"}) }));

    // midp is supported by the statement builder, so it must not be unsupported.
    BOOST_CHECK(!contains_pred(plan.unsupported_predicates, "midp"));
}

/**
 * @brief variable_indices are the declared-variable indices in declared order.
 */
BOOST_AUTO_TEST_CASE(variable_indices_basic) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C"},
                { pat("coll", {"A", "B", "C"}) },
                { pat("coll", {"A", "B", "C"}) }));

    const PlannedPredicate* p = find_pred(plan.candidate_generators, "coll");
    BOOST_REQUIRE(p != nullptr);
    BOOST_REQUIRE_EQUAL(p->variable_indices.size(), 3u);
    BOOST_CHECK_EQUAL(p->variable_indices[0], 0u);
    BOOST_CHECK_EQUAL(p->variable_indices[1], 1u);
    BOOST_CHECK_EQUAL(p->variable_indices[2], 2u);
}

/**
 * @brief Indices follow first appearance in the pattern, not declared order.
 */
BOOST_AUTO_TEST_CASE(variable_indices_follow_pattern_order) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C"},
                { pat("coll", {"C", "A", "B"}) },      // pattern order: C, A, B
                { pat("coll", {"A", "B", "C"}) }));

    const PlannedPredicate* p = find_pred(plan.candidate_generators, "coll");
    BOOST_REQUIRE(p != nullptr);
    BOOST_REQUIRE_EQUAL(p->variable_indices.size(), 3u);
    BOOST_CHECK_EQUAL(p->variable_indices[0], 2u);  // C
    BOOST_CHECK_EQUAL(p->variable_indices[1], 0u);  // A
    BOOST_CHECK_EQUAL(p->variable_indices[2], 1u);  // B
}

/**
 * @brief A variable repeated within a pattern appears once, at first appearance.
 */
BOOST_AUTO_TEST_CASE(variable_indices_dedup_repeated_variable) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C"},
                { pat("cong", {"A", "B", "A", "C"}) },  // A repeated
                { pat("coll", {"A", "B", "C"}) }));

    const PlannedPredicate* p = find_pred(plan.candidate_generators, "cong");
    BOOST_REQUIRE(p != nullptr);
    BOOST_REQUIRE_EQUAL(p->variable_indices.size(), 3u);  // A, B, C (not 4)
    BOOST_CHECK_EQUAL(p->variable_indices[0], 0u);  // A
    BOOST_CHECK_EQUAL(p->variable_indices[1], 1u);  // B
    BOOST_CHECK_EQUAL(p->variable_indices[2], 2u);  // C
}

/**
 * @brief Constant arguments are excluded from variable_indices but kept in args.
 */
BOOST_AUTO_TEST_CASE(variable_indices_exclude_constants) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C", "D"},
                { pat("rconst", {"A", "B", "C", "D", "1/2"}) },  // 1/2 is a constant
                { pat("coll", {"A", "B", "C"}) }));

    const PlannedPredicate* p = find_pred(plan.validators, "rconst");
    if (p == nullptr) {  // depending on metadata, rconst may be a filter
        p = find_pred(plan.candidate_filters, "rconst");
    }
    BOOST_REQUIRE(p != nullptr);
    BOOST_REQUIRE_EQUAL(p->variable_indices.size(), 4u);  // A,B,C,D only
    BOOST_CHECK_EQUAL(p->variable_indices[3], 3u);
    // The constant survives in the pattern itself.
    BOOST_CHECK_EQUAL(p->pattern.args.back(), "1/2");
}

/**
 * @brief Every hypothesis and conclusion is classified into exactly one bucket.
 */
BOOST_AUTO_TEST_CASE(every_predicate_classified_once) {
    RuleSchema s = schema({"A", "B", "C", "D"},
            { pat("coll", {"A", "B", "C"}),
            pat("ncoll", {"A", "B", "D"}) },
            { pat("cong", {"A", "B", "C", "D"}) });
    RulePlan plan = build_rule_plan(s);

    const size_t total = plan.candidate_generators.size()
        + plan.validators.size()
        + plan.candidate_filters.size()
        + plan.unsupported_predicates.size();
    BOOST_CHECK_EQUAL(total, s.hypotheses.size() + s.conclusions.size());
}

/**
 * @brief Planned predicates carry a positive base cost from the metadata table.
 */
BOOST_AUTO_TEST_CASE(generator_has_positive_base_cost) {
    RulePlan plan = build_rule_plan(
            schema({"A", "B", "C"},
                { pat("coll", {"A", "B", "C"}) },
                { pat("coll", {"A", "B", "C"}) }));

    const PlannedPredicate* p = find_pred(plan.candidate_generators, "coll");
    BOOST_REQUIRE(p != nullptr);
    BOOST_CHECK_GT(p->metadata.base_cost, 0u);
}

BOOST_AUTO_TEST_SUITE_END()
