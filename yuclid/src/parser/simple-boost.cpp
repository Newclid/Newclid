/**
   Copyright 2025 Concordance Inc. dba Harmonic

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
#include "parser/simple.hpp"
#include "problem.hpp"
#include "type/point.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/equal_angles.hpp"
#include "statement/para.hpp"
#include "statement/perp.hpp"
#include "config_options.hpp"
#include <stdexcept>
#include <boost/parser/parser.hpp>

using namespace std;

namespace bp = boost::parser;
namespace he = Yuclid;

static auto const grammar = [] {
  auto const is_alpha = bp::char_([&](char c) { return std::isalpha(static_cast<unsigned char>(c)); });
  auto const is_alnum = bp::char_([&](char c) { return std::isalnum(static_cast<unsigned char>(c)); });

  // Parser for a point name string (e.g., "A", "P1").
  // This part still produces a std::string.
  auto const point_name_string_parser = is_alpha >> *is_alnum;

  // Custom rule/transformation to emit a `Yuclid::point` object.
  // When point_name_string_parser matches a string, this rule takes that string
  // and constructs a `Yuclid::point` from it.
  auto const point_object_parser =
    bp::transform([](std::string const& s) { return he::point(s); })
    [point_name_string_parser];
  
  auto const coll_rule =
    bp::transform(
                  [](const auto &attr) {
                    return static_cast<unique_ptr<he::statement>>
                      (make_unique<he::coll>(attr[0], attr[1], attr[2]));
                  })
    [bp::lit("coll") > bp::repeat(3)[point_object_parser]];

  auto const cong_rule =
    bp::transform(
                  [](const auto &attr) {
                    return static_cast<unique_ptr<he::statement>>
                      (make_unique<he::DistEqDist>
                       (he::DistEqDist({attr[0], attr[1]}, {attr[2], attr[3]})));
                  })
    [bp::lit("cong") > bp::repeat(4)[point_object_parser]];

  auto const para_rule =
    bp::transform(
                  [](const auto &attr) {
                    return static_cast<unique_ptr<he::statement>>
                      (make_unique<he::para>
                       (he::para({attr[0], attr[1]}, {attr[2], attr[3]})));
                  })
    [bp::lit("para") > bp::repeat(4)[point_object_parser]];

  auto const perp_rule =
    bp::transform(
                  [](const auto &attr) {
                    return static_cast<unique_ptr<he::statement>>
                      (make_unique<he::perp>
                       (he::perp({attr[0], attr[1]}, {attr[2], attr[3]})));
                  })
    [bp::lit("perp") > bp::repeat(4)[point_object_parser]];

  auto const equal_angles_rule =
    bp::transform(
                  [](const auto &attr) {
                    return static_cast<unique_ptr<he::statement>>
                      (make_unique<he::equal_angles>
                       (he::equal_angles({attr[0], attr[1], attr[2]},
                                    {attr[3], attr[3], attr[4]})));
                  })
    [bp::lit("equal_angles") > bp::repeat(6)[point_object_parser]];


  const auto statement_rule =
    coll_rule
    | cong_rule
    | para_rule
    | perp_rule
    | equal_angles_rule;

  const auto name_line_rule =
    (bp::lit("name") > *(!bp::eol >> bp::char_) >> bp::eol)
    [([](const auto &name) { he::problem::set_name(name); })];

  const auto point_line_rule =
    (bp::lit("point") > point_name_string_parser > bp::double_ > bp::double_)
    [(
      [](const auto &args) {
        he::problem::add_point(bp::get<0>(args), get<1>(args), get<2>(args));
      }
      )];
                                                                              
  const auto assume_line_rule =
    bp::lit("assume") > statement_rule
    [([](auto pred) { he::problem::add_hypothesis(std::move(pred)); })];

  const auto assert_line_rule =
    bp::lit("prove") > statement_rule
    [([](auto pred) { he::problem::add_goal(std::move(pred)); })];

  const auto line_rule = name_line_rule | point_line_rule | assume_line_rule | assert_line_rule;

  return *line_rule;
 }();


namespace Yuclid {
  void parse_input_simple() {
    auto &is = ConfigOptions::get_istream();
    string s(std::istreambuf_iterator<char>(is), {});
    auto result = bp::parse(s, bp::ws, grammar);
    if (!result) {
      throw runtime_error("Failed to parse file");
    }
  }
}
