#define BOOST_TEST_MODULE custom_rule_integration_test

#include <boost/test/unit_test.hpp>

#include "matchers/generic_rule_matcher.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp" 
#include "config_options.hpp"
#include "solver/ddar_solver.hpp"
#include "solver/theorem_application.hpp"
#include "solver/statement_proof.hpp"
#include "ar/reduced_equation.hpp"
#include "problem.hpp"
#include "rules/rule_schema.hpp"
#include "type/point.hpp"
#include "theorem.hpp"

using namespace std;
using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(custom_rule_integration_test)

/**
 * @brief Test case for a custom rule solving the problem given
 * The custom rule assumes that congruence implies collinearity.
 * By making a geometrically false rule, the test ensures that the problem wont be solved by the already existing theorems.
 * The points in the problem are setup so that this is also numerically true.
 */
BOOST_AUTO_TEST_CASE(custom_rule_solves_problem) {
    Problem prob;
    (void)prob.add_point("A", 0.0, 0.0);
    (void)prob.add_point("B", 1.0, 0.0);
    (void)prob.add_point("C", -1.0, 0.0);

    prob.add_hypothesis(std::make_unique<DistEqDist>(
        Dist(Point(0, &prob), Point(1, &prob)), 
        Dist(Point(0, &prob), Point(2, &prob))
    ));
    
    prob.add_goal(std::make_unique<Collinear>(
        Point(0, &prob), Point(1, &prob), Point(2, &prob)
    ));

    RuleSchema schema;
    schema.id = "cong_implies_coll_rule";
    schema.variables = {"X", "Y", "Z"};
    
    RulePredicatePattern hyp = {"cong", {"X", "Y", "X", "Z"}};
    schema.hypotheses.push_back(hyp);
    
    RulePredicatePattern conc = {"coll", {"X", "Y", "Z"}};
    schema.conclusions.push_back(conc);

    std::vector<RuleSchema> custom_rules = { schema };

    // Run the Solver
    Config::Solver config;
    DDARSolver solver(&prob, &config, custom_rules);
    
    bool solved = solver.run(10); // Run for up to 10 levels
    
    BOOST_REQUIRE(solved);

    std::ostringstream json_output;
    solver.print_json(json_output);
    std::string output_str = json_output.str();

    // Verify the custom rule was used to reach the goal
    BOOST_CHECK(output_str.find("cong_implies_coll_rule") != std::string::npos);
}

BOOST_AUTO_TEST_SUITE_END()