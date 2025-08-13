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
#include "config_options.hpp"
#include "parser/simple.hpp"

#include <cmath>
#include "statement/circumcenter.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/congruent_triangles.hpp"
#include "statement/cyclic.hpp"
#include "statement/diff_side.hpp"
#include "statement/dist_eq.hpp"
#include "statement/eqratio.hpp"
#include "statement/equal_angles.hpp"
#include "statement/equal_line_angles.hpp"
#include "statement/line_angle_eq.hpp"
#include "statement/midpoint.hpp"
#include "statement/obtuse_angle.hpp"
#include "statement/para.hpp"
#include "statement/perp.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "statement/same_clock.hpp"
#include "statement/same_side.hpp"
#include "statement/similar_triangles.hpp"
#include "statement/squared_dist_eq.hpp"
#include "problem.hpp"
#include "type/dist.hpp"
#include "type/point.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"
#include <algorithm>
#include <format>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>

using namespace std;

namespace Yuclid {
  Problem parse_input_simple(istream &input) {
    Problem prob;
    auto get_point = [&prob](istringstream &str) -> Point {
      string name;
      str >> name;
      return prob.find_point(name);
    };
    auto get_dist = [&get_point](istringstream &str) -> Dist {
      return {get_point(str), get_point(str)};
    };
    auto get_squared_dist = [&get_point](istringstream &str) -> SquaredDist {
      return {get_point(str), get_point(str)};
    };
    auto get_angle = [&get_point](istringstream &str) -> Angle {
      return {get_point(str), get_point(str), get_point(str)};
    };
    auto get_slope_angle = [&get_point](istringstream &str) -> SlopeAngle {
      return {get_point(str), get_point(str)};
    };
    auto get_triangle = [&get_point](istringstream &str) -> Triangle {
      return {get_point(str), get_point(str), get_point(str)};
    };
    string line;
    while (getline(input, line)) {
      if (line.starts_with("name")) {
        prob.set_name(line.substr(5));
        continue;
      }
      if (line.starts_with("point")) {
        string name;
        double x = NAN;
        double y = NAN;
        istringstream(line) >> name >> name >> x >> y;
        std::ignore = prob.add_point(name, x, y);
        continue;
      }
      istringstream sstream(line);
      string action;
      string statement;
      sstream >> action >> statement;
      if (action != "assume" && action != "prove") {
        throw runtime_error(string("Incorrect line ") + line);
      }
      auto const act = [&](unique_ptr<Statement> &&statement) {
        if (action == "assume") {
          prob.add_hypothesis(std::move(statement));
        } else {
          prob.add_goal(std::move(statement));
        }
      };
      if (statement == "coll") {
        Point a = get_point(sstream);
        Point b = get_point(sstream);
        Point c = get_point(sstream);
        act(make_unique<Collinear>(a, b, c));
        string c_name;
        while (sstream >> c_name) {
          a = b;
          b = c;
          c = prob.find_point(c_name);
          act(make_unique<Collinear>(a, b, c));
        }
      } else if (statement == "cong") {
        Dist const d1 = get_dist(sstream);
        Dist const d2 = get_dist(sstream);
        act(make_unique<DistEqDist>(d1, d2));
      } else if (statement == "para") {
        act(make_unique<Parallel>(get_slope_angle(sstream), get_slope_angle(sstream)));
      } else if (statement == "perp") {
        act(make_unique<Perpendicular>(get_slope_angle(sstream), get_slope_angle(sstream)));
      } else if (statement == "eqangle" || statement == "equal_angles") {
        if (ranges::count(line, ' ') == 7) {
          act(make_unique<EqualAngles>(get_angle(sstream), get_angle(sstream)));
        } else if (ranges::count(line, ' ') == 9) {
          act(make_unique<EqualLineAngles>(get_slope_angle(sstream),
                                             get_slope_angle(sstream),
                                             get_slope_angle(sstream),
                                             get_slope_angle(sstream)));
        } else {
          throw runtime_error(format("Incorrect line {}, unexpected number of spaces", line));
        }
      } else if (statement == "eqratio") {
        act(make_unique<EqualRatios>(get_dist(sstream), get_dist(sstream),
                                 get_dist(sstream), get_dist(sstream)));
      } else if (statement == "cyclic") {
        auto a = get_point(sstream);
        auto b = get_point(sstream);
        auto c = get_point(sstream);
        auto d = get_point(sstream);
        act(make_unique<CyclicQuadrangle>(a, b, c, d));
        string d_name;
        while (sstream >> d_name) {
          a = b;
          b = c;
          c = d;
          d = prob.find_point(d_name);
          act(make_unique<CyclicQuadrangle>(a, b, c, d));
        }
      } else if (statement == "circumcenter" || statement == "circle") {
        auto o = get_point(sstream);
        auto a = get_point(sstream);
        auto b = get_point(sstream);
        auto c = get_point(sstream);
        act(make_unique<Circumcenter>(o, Triangle(a, b, c)));
        string c_name;
        while (sstream >> c_name) {
          a = b;
          b = c;
          c = prob.find_point(c_name);
          act(make_unique<Circumcenter>(o, Triangle(a, b, c)));
        }
      } else if (statement == "simtri") {
        auto t1 = get_triangle(sstream);
        auto t2 = get_triangle(sstream);
        act(make_unique<SimilarTriangles>(t1, t2, true));
      } else if (statement == "simtrir") {
        auto t1 = get_triangle(sstream);
        auto t2 = get_triangle(sstream);
        act(make_unique<SimilarTriangles>(t1, t2, false));
      } else if (statement == "contri") {
        auto t1 = get_triangle(sstream);
        auto t2 = get_triangle(sstream);
        act(make_unique<CongruentTriangles>(t1, t2, true));
      } else if (statement == "contrir") {
        auto t1 = get_triangle(sstream);
        auto t2 = get_triangle(sstream);
        act(make_unique<CongruentTriangles>(t1, t2, false));
      } else if (statement == "midp") {
        auto m = get_point(sstream);
        auto a = get_point(sstream);
        auto b = get_point(sstream);
        act(make_unique<Midpoint>(a, m, b));
      } else if (statement == "rconst") {
        auto d1 = get_dist(sstream);
        auto d2 = get_dist(sstream);
        NNRat r;
        sstream >> r;
        act(make_unique<RatioDistEquals>(d1, d2, r));
      } else if (statement == "r2const") {
        auto d1 = get_squared_dist(sstream);
        auto d2 = get_squared_dist(sstream);
        NNRat r;
        sstream >> r;
        act(make_unique<RatioSquaredDist>(d1, d2, r));
      } else if (statement == "lconst") {
        auto d = get_dist(sstream);
        NNRat r;
        sstream >> r;
        act(make_unique<DistEq>(d, r));
      } else if (statement == "l2const") {
        auto d = get_squared_dist(sstream);
        NNRat r;
        sstream >> r;
        act(make_unique<SquaredDistEq>(d, r));
      } else if (statement == "aconst") {
        auto a = get_slope_angle(sstream);
        auto b = get_slope_angle(sstream);
        Rat r;
        sstream >> r;
        act(LineAngleEq(a, b, r).normalize());
      } else if (statement == "sameclock") {
        auto l = get_triangle(sstream);
        auto r = get_triangle(sstream);
        act(make_unique<SameClock>(l, r));
      } else if (statement == "obtuse_angle") {
        act(make_unique<ObtuseAngle>(get_angle(sstream)));
      } else if (statement == "sameside" || statement == "nsameside") {
        auto a = get_point(sstream);
        auto b = get_point(sstream);
        auto c = get_point(sstream);
        auto d = get_point(sstream);
        auto e = get_point(sstream);
        auto f = get_point(sstream);
        if (statement == "sameside") {
          act(make_unique<SameSignDot>(a, b, c, d, e, f));
        } else {
          act(make_unique<DiffSignDot>(a, b, c, d, e, f));
        }
      } else {
        throw runtime_error(string("Unknown statement ") + statement);
      }
    }
    return prob;
  }
}
