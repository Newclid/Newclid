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

BOOST_AUTO_TEST_SUITE_END()
