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
#include "numbers/util.hpp"
#include "statement/coll.hpp"
#include "statement/obtuse_angle.hpp"
#include "statement/statement.hpp"
#include "typedef.hpp"
#include <memory>
#include <ostream>
#include <ranges>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {
  ObtuseAngle::ObtuseAngle(const Angle &ang) : m_angle(ang) { }

  ObtuseAngle::ObtuseAngle(const Collinear &arg) : m_angle(arg.a(), arg.b(), arg.c()) { }

  ObtuseAngle::ObtuseAngle(const vector<statement_arg>& args) :
    m_angle(get<Angle>(args.at(0))) {
  }

  string ObtuseAngle::name() const {
    return "obtuse_angle";
  }

  vector<Point> ObtuseAngle::points() const {
    return m_angle.points() | ranges::to<vector>();
  }

  unique_ptr<Statement> ObtuseAngle::normalize() const {
    if (m_angle.left() < m_angle.right()) {
      return clone();
    }
    return make_unique<ObtuseAngle>(-m_angle);
  }

  bool ObtuseAngle::check_nondegen() const {
    return m_angle.dot_product() < -EPS;
  }

  bool ObtuseAngle::check_equations() const {
    return true;
  }

  bool ObtuseAngle::numerical_only() const {
    return true;
  }

  vector<statement_arg> ObtuseAngle::args() const {
    return {m_angle};
  }

  unique_ptr<Statement> ObtuseAngle::clone() const {
    return make_unique<ObtuseAngle>(m_angle);
  }

  ostream &ObtuseAngle::print(ostream &out) const {
    return out << m_angle << " > π";
  }

}
