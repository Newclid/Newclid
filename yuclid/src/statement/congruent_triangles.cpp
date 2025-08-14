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
#include "statement/congruent_triangles.hpp"
#include "statement/cong.hpp"
#include "statement/similar_triangles.hpp"
#include "statement/statement.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"
#include <memory>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  CongruentTriangles::CongruentTriangles(const Triangle &t1,
                                           const Triangle &t2,
                                           bool same_clockwise) :
    SimilarTriangles(t1, t2, same_clockwise)
  { }

  CongruentTriangles::CongruentTriangles(const std::vector<statement_arg>& args) :
    SimilarTriangles(args)
  { }

  std::string CongruentTriangles::name() const {
    return same_clockwise() ? "contri" : "contrir";
  }

  std::unique_ptr<Statement> CongruentTriangles::normalize() const {
    auto normalize_base = dynamic_cast<const SimilarTriangles &>(*SimilarTriangles::normalize());
    return make_unique<CongruentTriangles>(normalize_base.left(), normalize_base.right(),
                                           normalize_base.same_clockwise());
  }

  bool CongruentTriangles::check_equations() const {
    return
      cong_ab().check_equations() &&
      cong_bc().check_equations() &&
      cong_ac().check_equations();
  }

  std::unique_ptr<Statement> CongruentTriangles::clone() const {
    return make_unique<CongruentTriangles>(*this);
  }

  DistEqDist CongruentTriangles::cong_ab() const {
    return {left().dist_ab(), right().dist_ab()};
  }

  DistEqDist CongruentTriangles::cong_bc() const {
    return {left().dist_bc(), right().dist_bc()};
  }

  DistEqDist CongruentTriangles::cong_ac() const {
    return {left().dist_ac(), right().dist_ac()};
  }
    

  std::ostream &CongruentTriangles::print(std::ostream &out) const {
    return out << left() << (same_clockwise() ? " ≅ " : " ≅r ") << right();
  }

} // namespace Yuclid
