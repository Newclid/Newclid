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
#include "ar/equation.hpp"
#include "ar/linear_combination.hpp"
#include "numbers/add_circle.hpp"
#include "numbers/root_rat.hpp"
#include "numbers/util.hpp"
#include "statement/angle_eq.hpp"
#include "statement/circumcenter.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/congruent_triangles.hpp"
#include "statement/cyclic.hpp"
#include "statement/eqn_statement.hpp"
#include "statement/eqratio.hpp"
#include "statement/equal_angles.hpp"
#include "statement/midpoint.hpp"
#include "statement/ncoll.hpp"
#include "statement/npara.hpp"
#include "statement/nperp.hpp"
#include "statement/not_equal.hpp"
#include "statement/obtuse_angle.hpp"
#include "statement/orthocenter.hpp"
#include "statement/para.hpp"
#include "statement/parallelogram.hpp"
#include "statement/perp.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/same_clock.hpp"
#include "statement/same_side.hpp"
#include "statement/similar_triangles.hpp"
#include "statement/statement.hpp"
#include "statement/thales.hpp"
#include "theorem.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"
#include <algorithm>
#include <boost/json/conversion.hpp>
#include <boost/json/value.hpp>
#include <boost/json/value_from.hpp>
#include <boost/log/trivial.hpp>
#include <cassert>
#include <cstddef>
#include <memory>
#include <ostream>
#include <ranges>
#include <utility>
#include <vector>

using namespace std;

namespace Yuclid {

  const std::vector<std::unique_ptr<Statement>> &Theorem::hypotheses() const {
    return m_hypotheses;
  }

  const std::vector<std::unique_ptr<Statement>> &Theorem::conclusions() const {
    return m_conclusions;
  }

  bool Theorem::check_hypotheses_numerically() const {
    return ranges::all_of(hypotheses(), [](const auto &p) { return p->check_numerically(); });
  }

  bool Theorem::check_hypotheses_nondeg_numerically() const {
    return ranges::all_of(hypotheses(), [](const auto &p) { return p->check_nondegen(); });
  }

  bool Theorem::check_conclusions_numerically() const {
    return ranges::all_of(conclusions(), [](const auto &p) { return p->check_numerically(); });
  }

  bool Theorem::check_numerically() const {
    return check_hypotheses_numerically() && check_conclusions_numerically();
  }

  Theorem& Theorem::add_similar_triangles_hypotheses(const SimilarTriangles& p) {
    return add_hypothesis<SameClock>(p.to_same_clock());
  }

  Theorem Theorem::equal_angles_of_cong(const Point &vertex,
                                        const Point &left,
                                        const Point &right) {
    Theorem thm("Angles in an isosceles triangle", "r13");
    thm
      .add_hypothesis<DistEqDist>(Dist(vertex, left), Dist(vertex, right))
      .add_conclusion<EqualAngles>(Angle(vertex, left, right), Angle(left, right, vertex));
    return thm;
  }

  Theorem Theorem::cong_of_equal_angles(const Point &vertex,
                                        const Point &left,
                                        const Point &right) {
    Theorem thm("Sides of an isosceles triangle", "r14");
    thm
      .add_hypothesis<EqualAngles>(Angle(vertex, left, right), Angle(left, right, vertex))
      .add_hypothesis<NonCollinear>(vertex, left, right)
      .add_conclusion<DistEqDist>(Dist(vertex, left), Dist(vertex, right));
    return thm;
  }

  Theorem Theorem::similar_triangles_properties(const SimilarTriangles &p) {
    Theorem thm("Properties of similar triangles", p.same_clockwise() ? "r52" : "r53");
    thm.add_hypothesis<SimilarTriangles>(p)
      .add_similar_triangles_hypotheses(p)
      .add_conclusion<EqualAngles>(p.equal_angles_abc())
      .add_conclusion<EqualAngles>(p.equal_angles_bca())
      .add_conclusion<EqualRatios>(p.eqratio_abbc())
      .add_conclusion<EqualRatios>(p.eqratio_abac());
    return thm;
  }

  Theorem Theorem::similar_triangles_of_sas(const SimilarTriangles &p) {
    Theorem thm("Similarity of triangles by 2 sides and an angle between them",
                p.same_clockwise() ? "r62" : "r63");
    thm
      .add_hypothesis<EqualRatios>(p.eqratio_abbc())
      .add_hypothesis<EqualAngles>(p.equal_angles_abc())
      .add_similar_triangles_hypotheses(p)
      .add_conclusion<SimilarTriangles>(p);
    return thm;
  }

  Theorem Theorem::similar_triangles_of_aa(const SimilarTriangles &p) {
    Theorem thm("Similarity of triangles by 2 angles",
                p.same_clockwise() ? "r34" : "r35");
    thm
      .add_hypothesis<EqualAngles>(p.equal_angles_abc())
      .add_hypothesis<EqualAngles>(p.equal_angles_acb())
      .add_similar_triangles_hypotheses(p)
      .add_conclusion<SimilarTriangles>(p);
    return thm;
  }

  Theorem Theorem::similar_triangles_of_sss(const SimilarTriangles &p) {
    Theorem thm("Similarity of triangles by proportionality of sides",
                p.same_clockwise() ? "r60" : "r61");
    thm
      .add_hypothesis<EqualRatios>(p.eqratio_abbc())
      .add_hypothesis<EqualRatios>(p.eqratio_abac())
      .add_similar_triangles_hypotheses(p)
      .add_conclusion<SimilarTriangles>(p);
    return thm;
  }

  Theorem Theorem::cyclic_of_equal_angles(const CyclicQuadrangle &p) {
    Theorem thm("Recognize a cyclic quadrilateral", "r04");
    thm
      .add_hypothesis<EqualAngles>(p.equal_angles_cad_cbd())
      .add_hypothesis<NonCollinear>(p.a(), p.c(), p.d())
      .add_conclusion<CyclicQuadrangle>(p);
    return thm;
  }

  Theorem Theorem::cyclic_properties(const CyclicQuadrangle &p) {
    Theorem thm("Properties of a cyclic quadrilateral", "r03");
    thm
      .add_hypothesis<CyclicQuadrangle>(p)
      .add_conclusion<EqualAngles>(p.equal_angles_cad_cbd())
      .add_conclusion<EqualAngles>(p.equal_angles_bad_bcd())
      .add_conclusion<EqualAngles>(p.equal_angles_abd_acd());
    return thm;
  }

  /** If `AB+BC=AC`, then `B` is between `A` and `C`.
   */
  Theorem Theorem::coll_of_add_length(const Collinear &p) {
    Equation<Dist> const eq =
      (LinearCombination<Dist>(Dist(p.a(), p.b())) +
       LinearCombination<Dist>(Dist(p.b(), p.c())) -
       LinearCombination<Dist>(Dist(p.a(), p.c())) == Rat(0));
    Theorem thm("If `AB+BC=AC`, then `B` is between `A` and `C`.", "ignore");
    thm
      .add_hypothesis<EqnStatement<Dist>>(eq)
      .add_conclusion<Collinear>(p);
    return thm;
  }

  /** If `B` is between `A` and `C`, then `AB+BC=AC`. */
  Theorem Theorem::add_length_of_between(const Collinear &p) {
    Theorem thm("If `B` is between `A` and `C`, then `AB+BC=AC`", "ignore");
    Equation<Dist> const eq =
      (LinearCombination<Dist>(Dist(p.a(), p.b())) +
       LinearCombination<Dist>(Dist(p.b(), p.c())) -
       LinearCombination<Dist>(Dist(p.a(), p.c())) == Rat(0));
    thm
      .add_hypothesis<Collinear>(p)
      .add_hypothesis<ObtuseAngle>(p)
      .add_conclusion<EqnStatement<Dist>>(eq);
    return thm;
  }

  /** If `AB||BC`, then `A`, `B`, `C` are collinear. */
  Theorem Theorem::coll_of_para(const Collinear &c) {
    Theorem thm("If `AB||BC`, then `A`, `B`, `C` are collinear.", "r28");
    thm
      .add_hypothesis<Parallel>(SlopeAngle(c.a(), c.b()), SlopeAngle(c.b(), c.c()))
      .add_conclusion<Collinear>(c.a(), c.b(), c.c());
    return thm;
  }

  /** If `A`, `B`, `C` are collinear, then the lines `AB`, `BC`, and `AC` are the same.
      We write it as `AB||BC`, `AB||AC`. */
  Theorem Theorem::para_of_coll(const Collinear &c) {
    Theorem thm("If `A`, `B`, `C` are collinear, then `AB||BC` and `AB||AC`.", "r82");
    thm
      .add_hypothesis<Collinear>(c.a(), c.b(), c.c())
      .add_hypothesis<NotEqual>(c.a(), c.b())
      .add_hypothesis<NotEqual>(c.a(), c.c())
      .add_hypothesis<NotEqual>(c.b(), c.c())
      .add_conclusion<Parallel>(SlopeAngle(c.a(), c.b()), SlopeAngle(c.b(), c.c()))
      .add_conclusion<Parallel>(SlopeAngle(c.a(), c.b()), SlopeAngle(c.a(), c.c()));
    return thm;
  }

  /** If `AB \perp CD`, then `AC^2+BD^2=AD^2+BC^2`. */
  Theorem Theorem::sum_squares_of_perp(const Perpendicular &p) {
    Theorem thm("AB ⟂ CD implies AC^2+BD^2=AD^2+BC^2", "ignore");
    LinearCombination<SquaredDist> lhs;
      lhs += LinearCombination<SquaredDist>
        ({p.left().left(), p.right().left()});
      lhs -= LinearCombination<SquaredDist>
        ({p.left().left(), p.right().right()});
      lhs -= LinearCombination<SquaredDist>
        ({p.left().right(), p.right().left()});
      lhs += LinearCombination<SquaredDist>
        ({p.left().right(), p.right().right()});
    thm
      .add_hypothesis<Perpendicular>(p)
      .add_hypothesis<NotEqual>(p.left().left(), p.right().left())
      .add_hypothesis<NotEqual>(p.left().left(), p.right().right())
      .add_hypothesis<NotEqual>(p.left().right(), p.right().left())
      .add_hypothesis<NotEqual>(p.left().right(), p.right().right())
      .add_conclusion<EqnStatement<SquaredDist>>(lhs == Rat(0));
    return thm;
  }

  /** If `AC^2 + BD^2 = AD^2 + BC^2`, then `AB \perp CD`. */
  Theorem Theorem::perp_of_sum_squares(const Perpendicular &p) {
    Theorem thm("If `AC^2 + BD^2 = AD^2 + BC^2`, then `AB \\perp CD`.", "ignore");
    LinearCombination<SquaredDist> lhs;
      lhs += LinearCombination<SquaredDist>
        ({p.left().left(), p.right().left()});
      lhs -= LinearCombination<SquaredDist>
        ({p.left().left(), p.right().right()});
      lhs -= LinearCombination<SquaredDist>
        ({p.left().right(), p.right().left()});
      lhs += LinearCombination<SquaredDist>
        ({p.left().right(), p.right().right()});
    thm
      .add_hypothesis<EqnStatement<SquaredDist>>(lhs == Rat(0))
      .add_hypothesis<NotEqual>(p.left().left(), p.right().left())
      .add_hypothesis<NotEqual>(p.left().left(), p.right().right())
      .add_hypothesis<NotEqual>(p.left().right(), p.right().left())
      .add_hypothesis<NotEqual>(p.left().right(), p.right().right())
      .add_conclusion<Perpendicular>(p);
    return thm;
  }

  Theorem Theorem::pythagoras_of_perp(const Angle &ang) {
    Theorem thm("Pythagoras theorem of perpendicularity", "ignore");
    LinearCombination<SquaredDist> lhs;
    lhs += LinearCombination<SquaredDist>({ang.vertex(), ang.left()});
    lhs += LinearCombination<SquaredDist>({ang.vertex(), ang.right()});
    lhs -= LinearCombination<SquaredDist>({ang.left(), ang.right()});
    thm
      .add_hypothesis<NotEqual>(ang.vertex(), ang.left())
      .add_hypothesis<NotEqual>(ang.vertex(), ang.right())
      .add_hypothesis<Perpendicular>(SlopeAngle(ang.vertex(), ang.left()),
                                     SlopeAngle(ang.vertex(), ang.right()))
      .add_conclusion<EqnStatement<SquaredDist>>(lhs == Rat(0));
    return thm;
  }

  Theorem Theorem::pythagoras_of_sum_squares(const Angle &ang) {
    Theorem thm("Pythagoras theorem of sum of squares", "ignore");
    LinearCombination<SquaredDist> lhs;
    lhs += LinearCombination<SquaredDist>({ang.vertex(), ang.left()});
    lhs += LinearCombination<SquaredDist>({ang.vertex(), ang.right()});
    lhs -= LinearCombination<SquaredDist>({ang.left(), ang.right()});
    thm
      .add_hypothesis<NotEqual>(ang.vertex(), ang.left())
      .add_hypothesis<NotEqual>(ang.vertex(), ang.right())
      .add_hypothesis<EqnStatement<SquaredDist>>(lhs == Rat(0))
      .add_conclusion<Perpendicular>(SlopeAngle(ang.vertex(), ang.left()),
                                     SlopeAngle(ang.vertex(), ang.right()));
    return thm;
  }

  Theorem Theorem::rotate_equal_ratio_of_same_side(const Collinear &left, const Collinear &right) {
    Theorem thm("Resolution of ratios for collinear points", "r71");
    thm
      .add_hypothesis<Collinear>(left)
      .add_hypothesis<Collinear>(right)
      .add_hypothesis<SameSignDot>(left, right)
      .add_hypothesis<EqualRatios>(Dist(left.a(), left.b()), Dist(left.a(), left.c()),
                                Dist(right.a(), right.b()), Dist(right.a(), right.c()))
      .add_conclusion<EqualRatios>(Dist(left.a(), left.b()), Dist(left.b(), left.c()),
                              Dist(right.a(), right.b()), Dist(right.b(), right.c()));
    return thm;
  }

  Theorem Theorem::circumcenter_of_cong(const Circumcenter &p) {
    Theorem thm("Definition of circumcenter", "r73");
    thm
      .add_hypothesis<DistEqDist>(p.cong_ab())
      .add_hypothesis<DistEqDist>(p.cong_bc())
      .add_conclusion<Circumcenter>(p);
    return thm;
  }

  Theorem Theorem::cong_of_circumcenter(const Circumcenter &p) {
    return circumcenter_of_cong(p).converse("Definition of circumcenter", "r72");
  }

  Theorem Theorem::arc_of_circumcenter(const Circumcenter &p) {
    Theorem thm("Arc angle and central angle", "ignore");
    thm.add_hypothesis<Circumcenter>(p);
    for (const auto &t : p.triangle().cyclic_rotations()) {
      Equation<Angle> eqn =
        Equation<Angle>::sub_eq_const({t.a(), t.b(), t.c()}, {p.center(), t.a(), t.c()},
                                      AddCircle<Rat>(Rat(1, 2)));
      thm.add_conclusion<EqnStatement<Angle>>(std::move(eqn));
    }
    return thm;
  }

  Theorem Theorem::circumcenter_of_arc(const Circumcenter &p) {
    Theorem thm("Circumcenter of arc's angle", "ignore");
    Equation<Angle> eqn =
      Equation<Angle>::sub_eq_const({p.a(), p.b(), p.c()}, {p.center(), p.a(), p.c()},
                                    AddCircle<Rat>(Rat(1, 2)));
    thm
      .add_hypothesis<DistEqDist>(p.cong_ac())
      .add_hypothesis<EqnStatement<Angle>>(std::move(eqn))
      .add_conclusion<Circumcenter>(p);
    return thm;
  }

  Theorem Theorem::thales_para_of_eqratio(const Thales &p) {
    Theorem thm("Thales Theorem 3", "r41");
    thm
      .add_hypothesis<Collinear>(p.coll_left())
      .add_hypothesis<Collinear>(p.coll_right())
      .add_hypothesis<Parallel>(p.para_bc())
      .add_hypothesis<EqualRatios>(p.coll_left().eqratio_ab_ac(p.coll_right()))
      .add_hypothesis<SameSignDot>(p.coll_left(), p.coll_right())
      .add_conclusion<Parallel>(p.para_ab());
    return thm;
  }

  /** If `A`, `B`, `C` are collinear, as well as `A'`, `B'`, `C'`,
      and `AA' || BB' || CC'`, then `AB:BC=A'B':B'C'` and `AB:AC=A'B':A'C'`.
  */
  Theorem Theorem::thales_eqratio_of_para(const Thales &p) {
    Theorem thm("Thales Theorem 4", "r42");
    thm
      .add_hypothesis<Collinear>(p.coll_left())
      .add_hypothesis<Collinear>(p.coll_right())
      .add_hypothesis<Parallel>(p.para_ab())
      .add_hypothesis<Parallel>(p.para_bc())
      .add_hypothesis<NonCollinear>(p.coll_left().a(), p.coll_right().a(), p.coll_left().b())
      .add_conclusion<EqualRatios>(p.coll_left().eqratio_ab_bc(p.coll_right()))
      .add_conclusion<EqualRatios>(p.coll_left().eqratio_ab_ac(p.coll_right()));
    return thm;
  }

  Theorem Theorem::sum_squares_of_midpoint(const Midpoint &p, const Point &pt) {
    Theorem thm("Sum of squares for a median", "ignore");
    Equation<SquaredDist> eq =
      (LinearCombination<SquaredDist>({pt, p.middle()}, 4) +
       LinearCombination<SquaredDist>({p.left(), p.right()}, 1) -
       LinearCombination<SquaredDist>({pt, p.left()}, 2) -
       LinearCombination<SquaredDist>({pt, p.right()}, 2) == Rat());
    thm
      .add_hypothesis<DistEqDist>(p.to_cong())
      .add_hypothesis<Collinear>(p.to_coll())
      .add_conclusion<EqnStatement<SquaredDist>>(std::move(eq));
    return thm;
  }

  Theorem Theorem::converse(const std::string_view &name,
                            const string_view &newclid_rule) const {
    Theorem thm(name, newclid_rule);
    thm.m_hypotheses =
      m_conclusions
      | views::transform([](const unique_ptr<Statement>& p) { return p->clone(); })
      | ranges::to<vector>();
    thm.m_conclusions =
      m_hypotheses
      | views::transform([](const unique_ptr<Statement>& p) { return p->clone(); })
      | ranges::to<vector>();
    return thm;
  }

  Theorem::Theorem(std::string_view name, std::string_view newclid_id) :
    m_name(name), m_newclid_rule(newclid_id)
  {}

  Theorem Theorem::triangle_bisector_of_equal_angles(const Point &point,
                                                     const Angle &angle) {
    Theorem thm("Property of a bisector in a triangle.", "r12");
    thm
      .add_hypothesis<EqualAngles>
      (Angle(angle.left(), angle.vertex(), point),
       Angle(point, angle.vertex(), angle.right()))
      .add_hypothesis<NonCollinear>(angle.left(), angle.vertex(), angle.right())
      .add_hypothesis<Collinear>(angle.left(), point, angle.right())
      .add_conclusion<EqualRatios>(Dist(point, angle.left()),
                                   Dist(point, angle.right()),
                                   Dist(angle.vertex(), angle.left()),
                                   Dist(angle.vertex(), angle.right()));
    return thm;
  }

  Theorem Theorem::triangle_bisector_of_eqratio(const Point& point,
                                                const Angle& angle) {
    Theorem thm("Property of a bisector in a triangle.", "r11");
    thm
      .add_hypothesis<NonCollinear>(angle.left(), angle.vertex(), angle.right())
      .add_hypothesis<Collinear>(angle.left(), point, angle.right())
      .add_hypothesis<EqualRatios>(Dist(point, angle.left()),
                                   Dist(point, angle.right()),
                                   Dist(angle.vertex(), angle.left()),
                                   Dist(angle.vertex(), angle.right()))
      .add_conclusion<EqualAngles>
      (Angle(angle.left(), angle.vertex(), point),
       Angle(point, angle.vertex(), angle.right()));
    return thm;
  }

  Theorem Theorem::equal_angles_of_cong_cyclic(Point a, Point b, Point c, Point d) {
    Theorem thm("Congruent chords have equal arc measure", "r80");
    thm
      .add_hypothesis<CyclicQuadrangle>(a, b, c, d)
      .add_hypothesis<DistEqDist>(Dist(a, b), Dist(c, d))
      .add_hypothesis<NonParallel>(SlopeAngle(a, c), SlopeAngle(b, d))
      .add_conclusion<EqualAngles>(Angle(a, c, b), Angle(c, b, d));
    return thm;
  }

  Theorem Theorem::equal_angles_of_iso_trapezoid(Point a, Point b, Point c, Point d) {
    Theorem thm("Equal angles in an iso trapezoid", "r91");
    thm
      .add_hypothesis<DistEqDist>(Dist(a, b), Dist(c, d))
      .add_hypothesis<Parallel>(SlopeAngle(a, d), SlopeAngle(b, c))
      .add_hypothesis<NonParallel>(SlopeAngle(a, b), SlopeAngle(c, d))
      .add_conclusion<EqualAngles>(Angle(a, c, b), Angle(c, b, d));
    return thm;
  }


  Theorem Theorem::parallelogram_law(const Parallelogram &p) {
    Theorem thm("Parallelogram law", "ignore");
    thm
      .add_hypothesis<Parallel>(p.para_ab_cd())
      .add_hypothesis<Parallel>(p.para_ad_bc())
      .add_conclusion<EqnStatement<SquaredDist>>(p.parallelogram_law_eqn());
    return thm;
  }

  Theorem Theorem::orthocenter(const IsOrthocenter &p) {
    Theorem thm("Orthocenter theorem", "r43");
    thm
      .add_hypothesis<Perpendicular>(p.perp_a())
      .add_hypothesis<Perpendicular>(p.perp_b())
      .add_conclusion<Perpendicular>(p.perp_c());
    return thm;
  }

  Theorem Theorem::midpoint_ratio_dist(const Midpoint &p) {
    Theorem thm ("Midpoint splits in two", "r51");
    thm
      .add_hypothesis<Midpoint>(p)
      .add_conclusion<RatioDistEquals>(Dist(p.left(), p.middle()),
                                 Dist(p.left(), p.right()),
                                 NNRat(1, 2))
      .add_conclusion<RatioDistEquals>(Dist(p.right(), p.middle()),
                                 Dist(p.left(), p.right()),
                                 NNRat(1, 2));
    return thm;
  }

  Theorem Theorem::midpoint_of_coll_cong(const Midpoint &p) {
    Theorem thm("Definition of midpoint", "r54");
    thm
      .add_hypothesis<Collinear>(p.to_coll())
      .add_hypothesis<DistEqDist>(p.to_cong())
      .add_conclusion<Midpoint>(p);
    return thm;
  }

  Theorem Theorem::cong_of_midpoint(const Midpoint &p) {
    Theorem thm("Properties of midpoint (cong)", "r55");
    thm
      .add_hypothesis<Midpoint>(p)
      .add_conclusion<DistEqDist>(p.to_cong());
    return thm;
  }

  Theorem Theorem::coll_of_midpoint(const Midpoint &p) {
    Theorem thm("Properties of midpoint (coll)", "r56");
    thm
      .add_hypothesis<Midpoint>(p)
      .add_conclusion<Collinear>(p.to_coll());
    return thm;
  }

  Theorem Theorem::hypotenuse_is_diameter(const Midpoint &p, const Point &pt) {
    Theorem thm("Hypotenuse is diameter", "r19");
    thm
      .add_hypothesis<Perpendicular>(SlopeAngle(p.left(), pt), SlopeAngle(p.right(), pt))
      .add_hypothesis<Midpoint>(p)
      .add_conclusion<DistEqDist>(Dist(p.left(), p.middle()), Dist(pt, p.middle()));
    return thm;
  }

  Theorem Theorem::congruent_triangles_of_similar_triangles(const CongruentTriangles &p) {
    Theorem thm("Similarity without scaling", p.same_clockwise() ? "r68" : "r69");
    thm
      .add_hypothesis<SimilarTriangles>(p)
      .add_hypothesis<DistEqDist>(p.cong_ab())
      .add_conclusion<CongruentTriangles>(p);
    return thm;
  }

  Theorem Theorem::congruent_triangles_properties(const CongruentTriangles &p) {
    return congruent_triangles_of_similar_triangles(p).converse
      ("Congruent triangles are similar with coeff 1",
       (p.same_clockwise() ? "r77" : "r78"));
  }

  Theorem Theorem::incenter(const Point &point, const Angle &angle) {
    Theorem thm("Incenter theorem", "r46");
    thm
      .add_hypothesis<EqualAngles>(Angle(angle.vertex(), angle.left(), point),
                                   Angle(point, angle.left(), angle.right()))
      .add_hypothesis<EqualAngles>(Angle(angle.left(), angle.right(), point),
                                   Angle(point, angle.right(), angle.vertex()))
      .add_hypothesis<NonCollinear>(angle.left(), angle.vertex(), angle.right())
      .add_conclusion<EqualAngles>(Angle(angle.left(), angle.vertex(), point),
                                   Angle(point, angle.vertex(), angle.right()));
    return thm;
  }

  Theorem Theorem::cong_of_circumcenter_of_cyclic(const Circumcenter &p, const Point &pt) {
    Theorem thm("Recognize center of cyclic", "r49");
    thm
      .add_hypothesis<Circumcenter>(p)
      .add_hypothesis<CyclicQuadrangle>(pt, p.a(), p.b(), p.c())
      .add_conclusion<DistEqDist>(Dist(p.center(), p.a()), Dist(p.center(), pt));
    return thm;
  }

  Theorem Theorem::center_of_cyclic_of_cong_of_cong(const CyclicQuadrangle &p, const Point &pt) {
    Theorem thm("Recognize center of cyclic from cong", "r50");
    thm
      .add_hypothesis<CyclicQuadrangle>(p)
      .add_hypothesis<DistEqDist>(Dist(pt, p.a()), Dist(pt, p.b()))
      .add_hypothesis<DistEqDist>(Dist(pt, p.c()), Dist(pt, p.d()))
      .add_hypothesis<NonParallel>(SlopeAngle(p.a(), p.b()),
                             SlopeAngle(p.c(), p.d()))
      .add_conclusion<DistEqDist>(Dist(pt, p.a()), Dist(pt, p.c()));
    return thm;
  }

  Theorem Theorem::angle_bisector_meets_bisector(const Angle& ang, const Point &pt) {
    Theorem thm("Angle bisector meets side bisector on the circumcircle.", "r74");
    thm
      .add_hypothesis<EqualAngles>(Angle(ang.left(), ang.vertex(), pt),
                                    Angle(pt, ang.vertex(), ang.right()))
      .add_hypothesis<DistEqDist>(Dist(ang.left(), pt), Dist(ang.right(), pt))
      .add_hypothesis<NonCollinear>(ang.left(), ang.vertex(), ang.right())
      .add_hypothesis<NonPerpendicular>(SlopeAngle(ang.vertex(), pt),
                             SlopeAngle(ang.left(), ang.right()))
      .add_conclusion<CyclicQuadrangle>(pt, ang.left(), ang.vertex(), ang.right());
    return thm;
  }

  Point Theorem::max_point() const {
#ifdef __cpp_lib_ranges_concat
    // TODO: test that this #ifdef branch actually works
    return
      ranges::max(views::concat(m_hypotheses, m_conclusions)
                  | views::transform([](const auto &hyp) {
                    return hyp->points();
                  })
                  | views::join);
#else
    if (m_hypotheses.empty()) {
      return ranges::max(m_conclusions
                         | views::transform([](const auto &hyp) {
                           return hyp->points();
                         })
                         | views::join);

    }
    assert(!m_conclusions.empty());
    return
      std::max(ranges::max(m_hypotheses
                           | views::transform([](const auto &hyp) {
                             return hyp->points();
                           })
                           | views::join),
               ranges::max(m_conclusions
                           | views::transform([](const auto &hyp) {
                             return hyp->points();
                           })
                           | views::join));
#endif
  }

  Theorem Theorem::clone() const {
    Theorem thm(m_name, m_newclid_rule);
    thm.m_hypotheses =
      m_hypotheses
      | views::transform([](const unique_ptr<Statement>& p) { return p->clone(); })
      | ranges::to<vector>();
    thm.m_conclusions =
      m_conclusions
      | views::transform([](const unique_ptr<Statement>& p) { return p->clone(); })
      | ranges::to<vector>();
    return thm;
  }

  Theorem Theorem::equal_angles_of_sin_eq_sin(const EqualAngles &p) {
    Theorem thm("equal angles of sin eq sin", "ignore");
    Equation<SinOrDist> eq =
      Equation<SinOrDist>::sub_eq_const(SinOrDist(p.right_angle()),
                                          SinOrDist(p.left_angle()));
    thm
      .add_hypothesis<EqnStatement<SinOrDist>>(std::move(eq))
      .add_conclusion<EqualAngles>(p);
    return thm;
  }

  Theorem Theorem::sin_eq_sin_of_equal_angles(const EqualAngles &p) {
    return equal_angles_of_sin_eq_sin(p).converse("sin eq sin of equal angles", "ignore");
  }

  Theorem Theorem::law_of_sines(const Triangle &t) {
    Theorem thm("law of sines", "ignore");
    Equation<SinOrDist> eq = Equation<SinOrDist>::sub_eq_sub
      (SinOrDist(SquaredDist(t.dist_bc())), SinOrDist(t.angle_a()),
       SinOrDist(SquaredDist(t.dist_ac())), SinOrDist(t.angle_b()));
    thm
      .add_hypothesis<NonCollinear>(t.a(), t.b(), t.c())
      .add_conclusion<EqnStatement<SinOrDist>>(std::move(eq));
    return thm;
  }

  Theorem Theorem::sin_eq_of_angle_eq(const Angle &ang, size_t ind) {
    assert(ind < known_sin_squares().size());
    const auto [ang_val, sin_val] = known_sin_squares()[ind];
    Theorem thm("Sine of a known angle", "ignore");
    vector<unique_ptr<Statement>> const hypotheses;
    vector<unique_ptr<Statement>> const conclusions;
    Equation<SinOrDist> eqn =
      Equation<SinOrDist>(LinearCombination<SinOrDist>(SinOrDist(ang)),
                          RootRat(sin_val));
    thm
      .add_hypothesis<AngleEq>(ang, AddCircle<Rat>(ang_val))
      .add_conclusion<EqnStatement<SinOrDist>>(std::move(eqn));
    return thm;
  }

  Theorem Theorem::angle_eq_of_sin_eq(const Angle &ang, size_t ind) {
    return sin_eq_of_angle_eq(ang, ind)
      .converse("Find angle by its sine", "ignore");
  }

  Theorem Theorem::normalize() const {
    Theorem thm(m_name, m_newclid_rule);
    thm.m_hypotheses =
      m_hypotheses
      | views::transform([](const unique_ptr<Statement>& p) { return p->normalize(); })
      | ranges::to<vector>();
    thm.m_conclusions =
      m_conclusions
      | views::transform([](const unique_ptr<Statement>& p) { return p->normalize(); })
      | ranges::to<vector>();
    return thm;
  }

  std::ostream &operator<<(std::ostream &out, const Theorem &thm) {
    size_t n = thm.hypotheses().size();
    if (n > 0) {
      out << *thm.hypotheses()[0];
      for (size_t i = 1; i < n; ++ i) {
        out << ", " << *thm.hypotheses()[i];
      }
    }
    out << " ⊢[" << (thm.newclid_rule() == "ignore" ? thm.name() : thm.newclid_rule()) << "] ";
    n = thm.conclusions().size();
    if (n > 0) {
      out << *thm.conclusions()[0];
      for (size_t i = 1; i < n; ++ i) {
        out << ", " << *thm.conclusions()[i];
      }
    }
    return out;
  }

  void tag_invoke(boost::json::value_from_tag /*unused*/, boost::json::value& jv, const Theorem& p) {
    jv = {
      {"name", p.name()},
      {"newclid_rule", p.newclid_rule()},
      {"hypotheses", boost::json::value_from(p.hypotheses())},
      {"conclusions", boost::json::value_from(p.conclusions())}
    };
  }

}
