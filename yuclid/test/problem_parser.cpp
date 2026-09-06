#define BOOST_TEST_MODULE problem_parser_test

#include <boost/test/unit_test.hpp>
#include "parser/problem_parser.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/line_angle_eq.hpp"
#include "problem.hpp"
#include <sstream>
#include <string>

using namespace std;
using namespace Yuclid;

// These helpers generate a fake JGEX file in memory, run it through the parser, 
// and return the extracted ratio.

NNRat get_parsed_rconst(const std::string& rconst_val) {
    std::string jgex_input = 
        "point A 0 0\n"
        "point B 1 0\n"
        "point C 0 1\n"
        "point D 1 1\n"
        "assume rconst A B C D " + rconst_val + "\n"; 

    std::istringstream input_stream(jgex_input);
    Problem prob = parse_problem(input_stream);
    
    auto* stmt = dynamic_cast<RatioDistEquals*>(prob.hypotheses()[0].get());
    BOOST_REQUIRE(stmt != nullptr);
    
    auto args = stmt->args();
    return std::get<NNRat>(args[2]);
}

Rat get_parsed_aconst(const std::string& aconst_val) {
    std::string jgex_input = 
        "point A 0 0\n"
        "point B 1 0\n"
        "point C 0 1\n"
        "point D 1 1\n"
        "assume aconst A B C D " + aconst_val + "\n"; 

    std::istringstream input_stream(jgex_input);
    Problem prob = parse_problem(input_stream);
    
    auto* stmt = dynamic_cast<LineAngleEq*>(prob.hypotheses()[0].get());
    BOOST_REQUIRE(stmt != nullptr);
    
    auto args = stmt->args();
    return std::get<AddCircle<Rat>>(args[2]).number();
}

BOOST_AUTO_TEST_SUITE(parser_behavior_suite)


BOOST_AUTO_TEST_CASE(parser_normal_fraction) {
    NNRat ratio = get_parsed_rconst("5/2");
    BOOST_CHECK_EQUAL(ratio, NNRat(5, 2));
}

BOOST_AUTO_TEST_CASE(parser_behaviour_no_slash_integer) {
    NNRat ratio = get_parsed_rconst("3");

    BOOST_TEST_MESSAGE("Parser interpreted '3' as: " << ratio);
    // when there is no slash and no denominator, boost silently fails and defaults to 0/1
    BOOST_CHECK_EQUAL(ratio, NNRat(0, 1));
}

BOOST_AUTO_TEST_CASE(parser_behaviour_negative_integer) {
    Rat ratio = get_parsed_aconst("-1/3");
    
    BOOST_TEST_MESSAGE("Parser interpreted '-1/3' as: " << ratio);
    // these are represented as rotations on a circle and normalized, so -1/3 rotations is the same as 2/3 rotations
    BOOST_CHECK_EQUAL(ratio, Rat(2, 3));
}

BOOST_AUTO_TEST_CASE(parser_division_by_zero) {
    NNRat ratio = get_parsed_rconst("2/0");

    BOOST_TEST_MESSAGE("Parser interpreted '2/0' as: " << ratio);
    // when there is division by 0, boost silently fails and defaults to 0/1
    BOOST_CHECK_EQUAL(ratio, NNRat(0, 1));
}

BOOST_AUTO_TEST_CASE(parser_trailing_slash) {
    BOOST_REQUIRE_THROW(get_parsed_rconst("5/"), std::system_error);
}

BOOST_AUTO_TEST_CASE(parser_start_slash) {
    BOOST_REQUIRE_THROW(get_parsed_rconst("/5"), std::system_error);
}

BOOST_AUTO_TEST_CASE(parser_garbage_denominator) {
    BOOST_REQUIRE_THROW(get_parsed_rconst("5/abc"), std::system_error);
}

BOOST_AUTO_TEST_CASE(parser_garbage_numerator) {
    BOOST_REQUIRE_THROW(get_parsed_rconst("abc/5"), std::system_error);
}

BOOST_AUTO_TEST_SUITE_END()