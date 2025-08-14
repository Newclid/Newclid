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
#include <algorithm>
#include <memory>
#include <ranges>
#include "statement/statement.hpp"
#include "typedef.hpp"
#include "thales.hpp"
#include "coll.hpp"
#include "para.hpp"
#include <iostream>  // For debug/error messages (can be removed later)
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  Thales::Thales(const Collinear& b1, const Collinear& b2)
    : m_left(b1), m_right(b2) { }

  // Explicit constructor from vector<statement_arg>
  Thales::Thales(const vector<statement_arg>& args) :
    m_left(get<Point>(args.at(0)), get<Point>(args.at(1)), get<Point>(args.at(2))),
    m_right(get<Point>(args.at(3)), get<Point>(args.at(4)), get<Point>(args.at(5)))
  {}

  string Thales::name() const { return "thales"; }

  vector<Point> Thales::points() const {
    return {
      m_left.a(), m_left.b(), m_left.c(),
      m_right.a(), m_right.b(), m_right.c()
    };
  }

  unique_ptr<Statement> Thales::normalize() const {
    return make_unique<Thales>(ranges::min(permutations()));
  }

  Parallel Thales::para_ab() const {
    return {{m_left.a(), m_right.a()}, {m_left.b(), m_right.b()}};
  }

  Parallel Thales::para_ac() const {
    return {{m_left.a(), m_right.a()}, {m_left.c(), m_right.c()}};
  }

  Parallel Thales::para_bc() const {
    return {{m_left.b(), m_right.b()}, {m_left.c(), m_right.c()}};
  }

  Collinear Thales::coll_left() const {
    return m_left;
  }

  Collinear Thales::coll_right() const {
    return m_right;
  }

  bool Thales::check_nondegen() const {
    for (auto [left, right] :
           views::zip(m_left.cyclic_permutations(),
                      m_right.cyclic_permutations())) {
      if (left.is_between() != right.is_between()) {
        return false;
      }
    }
    return
      para_ab().check_nondegen() &&
      para_ac().check_nondegen() &&
      !Collinear(m_left.a(), m_left.b(), m_right.a()).check_equations();
  }

  bool Thales::check_equations() const {
    return
      m_left.check_equations() &&
      m_right.check_equations() &&
      para_ab().check_equations() &&
      para_bc().check_equations();
  }

  vector<statement_arg> Thales::args() const {
    return {m_left.a(), m_left.b(), m_left.c(), m_right.a(), m_right.b(), m_right.c()};
  }

  unique_ptr<Statement> Thales::clone() const {
    return make_unique<Thales>(*this);
  }

  Thales Thales::rotate() const {
    return {Collinear(m_left.b(), m_left.c(), m_left.a()),
            Collinear(m_right.b(), m_right.c(), m_right.a())};
  }

  ostream &Thales::print(ostream &out) const {
    return out << "thales(" << m_left << ", " << m_right << ")";
  }

} // namespace Yuclid
