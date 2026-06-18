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

BOOST_AUTO_TEST_SUITE_END()
