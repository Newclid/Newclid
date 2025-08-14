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
#include "circumcenter.hpp"
#include "cong.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"
#include <memory>
#include <ostream>
#include <stdexcept> // For std::invalid_argument
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  Circumcenter::Circumcenter(Point center, Triangle tri)
    : m_center(center), m_triangle(tri) {}

  Circumcenter::Circumcenter(const vector<statement_arg>& args) :
    m_center(get<Point>(args[0])),
    m_triangle(get<Triangle>(args[1]))
  {
    if (args.size() != 2) {
      throw invalid_argument("circumcenter constructor expects 2 arguments.");
    }
  }

  string Circumcenter::name() const { return "circle"; }

  DistEqDist Circumcenter::cong_ab() const {
    return {{center(), a()}, {center(), b()}};
  }

  DistEqDist Circumcenter::cong_bc() const {
    return {{center(), b()}, {center(), c()}};
  }

  DistEqDist Circumcenter::cong_ac() const {
    return {{center(), a()}, {center(), c()}};
  }

  vector<Point> Circumcenter::points() const {
    return {m_center, m_triangle.a(), m_triangle.b(), m_triangle.c()};
  }

  unique_ptr<Statement> Circumcenter::normalize() const {
    return make_unique<Circumcenter>(m_center, m_triangle.sorted());
  }

  bool Circumcenter::check_nondegen() const {
    return m_triangle.check_nondegen();
  }

  bool Circumcenter::check_equations() const {
    return cong_ab().check_equations() && cong_bc().check_equations();
  }

  vector<statement_arg> Circumcenter::args() const {
    return {m_center, m_triangle};
  }

  unique_ptr<Statement> Circumcenter::clone() const {
    return make_unique<Circumcenter>(*this); // Implementation of clone()
  }

  ostream &Circumcenter::print(ostream &out) const {
    return out << center().name() << " = circumcenter(▵" <<
      a().name() << " " << b().name() << " " << c().name() << ")";
  }
} // namespace Yuclid
