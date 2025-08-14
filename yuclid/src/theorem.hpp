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
#pragma once
#include <vector>
#include "statement/statement.hpp"

/** @file Theorem class and a list of theorems.

    Possible future extensions:

    - "half-true" converse theorems (see below);

    - Menelaus's theorem; AFAICT, Ceva's and other similar facts
      follow from it;
 */

namespace Yuclid {
  // Forward-declare some statements.
  class AngleEq;
  class Circumcenter;
  class Collinear;
  class DistEqDist;
  class CongruentTriangles;
  class CyclicQuadrangle;
  class Dist;
  class EqualAngles;
  class IsOrthocenter;
  class Midpoint;
  class Parallel;
  class Parallelogram;
  class Perpendicular;
  class SimilarTriangles;
  class Thales;

  class Theorem {
  public:
    Theorem(const Theorem &orig) = delete;
    Theorem(Theorem &&other) noexcept = default;

    /** Hypotheses of a theorem. */
    [[nodiscard]] const std::vector<std::unique_ptr<Statement>> &hypotheses() const;
    /** Conclusions of a theorem. */
    [[nodiscard]] const std::vector<std::unique_ptr<Statement>> &conclusions() const;

    /** Check if all the hypotheses are numerically correct. */
    [[nodiscard]] bool check_hypotheses_numerically() const;

    /** Check that the *inequality* hypotheses are numerically correct. */
    [[nodiscard]] bool check_hypotheses_nondeg_numerically() const;

    /** Check if all the conclusions are numerically correct. */
    [[nodiscard]] bool check_conclusions_numerically() const;

    /** Check if both hypotheses and conclusions are numerically correct. */
    [[nodiscard]] bool check_numerically() const;

    static Theorem equal_angles_of_cong(const Point& vertex, const Point& left, const Point& right);

    static Theorem cong_of_equal_angles(const Point& vertex, const Point& left, const Point& right);

    /** Corollaries of triangles being similar. */
    static Theorem similar_triangles_properties(const SimilarTriangles &p);

    /** If `|AB|:|BC|=|A'B'|:|B'C'|` and `∠ABC = ∠A'B'C'`,
        then `ABC` is similar to `A'B'C'`.

        This function should be called 3 times to get all cyclic permutations.

        TODO: Should we add the `|AB|:|BC|` + `∠CAB` version?
        It's a bit of cheating, but we can probably prove it with an extra construction anyway
        (if we trust the picture about inequalities).
    */
    static Theorem similar_triangles_of_sas(const SimilarTriangles &p);

    /** Given triangles `ABC` and `A'B'C'`,
        if `∠CAB = ∠C'A'B'` and `∠ABC = ∠A'B'C'`,
        then they're similar.

        This function should be called once,
        because the permutations have equivalent hypotheses,
        up to angle chase.
    */
    static Theorem similar_triangles_of_aa(const SimilarTriangles &p);

    /** If the corresponding sides of two triangles are proportional,
        then the triangles are similar.

        This function should be called once,
        because the permutations have equivalent hypotheses.
    */
    static Theorem similar_triangles_of_sss(const SimilarTriangles &p);

    /** If `∠CAD = ∠CBD`, then `ABCD` is a cyclic quadrilateral.

        This function should be called 3 times,
        once for each of `ABCD`, `ACBD`, `BCAD`.
        The other permutations are equivalent,
        up to angle chase.
     */
    static Theorem cyclic_of_equal_angles(const CyclicQuadrangle &p);

    /** If `ABCD` is a cyclic quadrilateral,
        then `∠CAD = ∠CBD`, `∠BAD = ∠BCD`,
        and `∠ABD = ∠ACD`.

        Similar equalities hold for other chords,
        but they follow from these three and the angle chase.
     */
    static Theorem cyclic_properties(const CyclicQuadrangle &p);

    /** If `AB+BC=AC`, then `B` is between `A` and `C`.
     */
    static Theorem coll_of_add_length(const Collinear &p);

    /** If `B` is between `A` and `C`, then `AB+BC=AC`. */
    static Theorem add_length_of_between(const Collinear &p);

    /** If `O` is the circumcenter of `ABC`,
        then `∠ABC + ∠CAO = π / 2`,
        and similarly for cyclic permutations.

        This is a way to say that `2∠ABC = ∠AOC`
        without multiplying by two or introducing new points.

        This theorem has multiple conclusions,
        so it suffices to call it once.
    */
    static Theorem arc_of_circumcenter(const Circumcenter &p);

    /** The converse of `arc_of_circumcenter`.

        If `OA=OC` and `∠ABC + ∠CAO = π / 2`,
        then `O` is the circumcenter of `ABC`.

        TODO: does it stay true, if we require `OA=OB`
        with the same angle equality instead?
     */
    static Theorem circumcenter_of_arc(const Circumcenter &p);

    /** Definition of a circumcenter. */
    static Theorem circumcenter_of_cong(const Circumcenter &p);

    /** Definition of a circumcenter. */
    static Theorem cong_of_circumcenter(const Circumcenter &p);

    /** If `AB \perp CD`, then `AC^2+BD^2=AD^2+BC^2`. */
    static Theorem sum_squares_of_perp(const Perpendicular &p);

    /** If `AC^2 + BD^2 = AD^2 + BC^2`, then `AB \perp CD`. */
    static Theorem perp_of_sum_squares(const Perpendicular &p);

    static Theorem pythagoras_of_perp(const Angle &ang);

    static Theorem pythagoras_of_sum_squares(const Angle &ang);

    /** If `B` is between `A` and `C`, `B'` is between `A'` and `C'`,
        and `AB:BC=A'B':B'C'`, then `AB:AC=A'B':A'C'. */
    static Theorem rotate_equal_ratio_of_same_side(const Collinear &left, const Collinear &right);

    /** If `A`, `B`, `C` are collinear, as well as `A'`, `B'`, `C'`,
        `AA' || BB'`, and `AB:BC=A'B':B'C'`, then `AA'||CC'`.

        This function should be called 3 times
        with cyclic permutations of the points.
    */
    static Theorem thales_para_of_eqratio(const Thales &p);

    /** If `A`, `B`, `C` are collinear, as well as `A'`, `B'`, `C'`,
        and `AA' || BB' || CC'`, then `AB:BC=A'B':B'C'` and `AB:AC=A'B':A'C'`.
    */
    static Theorem thales_eqratio_of_para(const Thales &p);

    /** If `AL` is the bisector (or the exterior bisector) of the triangle `ABC`,
        then `BL:LC=AB:AC`.
     */
    static Theorem triangle_bisector_of_equal_angles(const Point &point, const Angle &angle);

    static Theorem triangle_bisector_of_eqratio(const Point &point, const Angle &angle);

    /** If `ABCD` is a cyclic quadrilateral, `AB=CD`,
        and the chords `AB` and `CD` go in the same direction,
        then `∠ACB = ∠CAD`.

        The converse theorem follows from equality of triangles.
    */
    static Theorem equal_angles_of_cong_cyclic(Point a, Point b, Point c, Point d);

    static Theorem equal_angles_of_iso_trapezoid(Point a, Point b, Point c, Point d);

    static Theorem parallelogram_law(const Parallelogram &p);

    /** If `AM` is the median of `ABC`, then `4AM^2+BC^2 = 2AB^2+2AC^2`.
        In fact, this works for any point `A`, including those on the line `BC`.

        TODO: should we add the converse theorem? It's a bit of cheating,
        because there are 2 pts at this distance from `A` on `BC`,
        but we allow similar "trust the picture" tricks here and there.
    */
    static Theorem sum_squares_of_midpoint(const Midpoint &p, const Point &pt);

    /** If `AB||BC`, then `A`, `B`, `C` are collinear. */
    static Theorem coll_of_para(const Collinear &c);

    /** If `A`, `B`, `C` are collinear, then the lines `AB`, `BC`, and `AC` are the same.
        We write it as `AB||BC`, `AB||AC`. */
    static Theorem para_of_coll(const Collinear &c);

    /** If `\sin² α = \sin² β`, then `α = β` or `α = -β`.
     *
     * We match the right one of these two numerically.
     */
    static Theorem equal_angles_of_sin_eq_sin(const EqualAngles &p);

    /** If `α = β`, then `\sin² α = \sin² β`.
     */
    static Theorem sin_eq_sin_of_equal_angles(const EqualAngles &p);

    /** Law of sines for a triangle. */
    static Theorem law_of_sines(const Triangle &t);

    static Theorem sin_eq_of_angle_eq(const Angle &ang, size_t ind);
    static Theorem angle_eq_of_sin_eq(const Angle &ang, size_t ind);

    /**
     * @brief Orthocenter theorem.
     *
     * This theorem should be matched only if we don't use the "squared dists" AR table.
     */
    static Theorem orthocenter(const IsOrthocenter &p);

    static Theorem midpoint_ratio_dist(const Midpoint &p);
    static Theorem midpoint_of_coll_cong(const Midpoint &p);
    static Theorem cong_of_midpoint(const Midpoint &p);
    static Theorem coll_of_midpoint(const Midpoint &p);
    static Theorem hypotenuse_is_diameter(const Midpoint &p, const Point &pt);

    static Theorem congruent_triangles_of_similar_triangles(const CongruentTriangles &p);
    static Theorem congruent_triangles_properties(const CongruentTriangles &p);
    static Theorem incenter(const Point &point, const Angle &angle);

    static Theorem cong_of_circumcenter_of_cyclic(const Circumcenter &p, const Point &pt);
    static Theorem center_of_cyclic_of_cong_of_cong(const CyclicQuadrangle &p, const Point &pt);

    static Theorem angle_bisector_meets_bisector(const Angle& ang, const Point &pt);

    [[nodiscard]] Theorem normalize() const;

    Theorem() = default;

    [[nodiscard]] const std::string_view &name() const { return m_name; }
    [[nodiscard]] const std::string_view &newclid_rule() const { return m_newclid_rule; }
    [[nodiscard]] Theorem clone() const;

    /**
     * @brief Find the maximal (w.r.t. index) point used in a theorem.
     *
     * @return The maximal point used in the theorem.
     * @throws std::runtime_error if the theorem has no points.
     */
    [[nodiscard]] Point max_point() const;

  private:
    Theorem(std::string_view name, std::string_view newclid_id);

    /**
     * @brief Add a hypothesis to the theorem.
     *
     * This modifies the theorem in place.
     * If the new hypothesis is a `refl` statement, it gets ignored.
     */
    template <typename T, typename ... args_t>
    Theorem &add_hypothesis(args_t... args) {
      static_assert(std::is_base_of_v<Statement, T>);
      m_hypotheses.emplace_back
        (std::make_unique<T>(std::forward<args_t>(args)...));
      return *this;
    }

    /**
     * @brief Add common nondegenericity hypotheses for similar triangles.
     */
    Theorem& add_similar_triangles_hypotheses(const SimilarTriangles& p);

    /**
     * @brief Add a conclusion to the theorem.
     *
     * This modifies the theorem in place.
     * If the new conclusion is a `refl` statement, it gets ignored.
     */
    template <typename T, typename ... args_t>
    Theorem &add_conclusion(args_t... args) {
      static_assert(std::is_base_of_v<Statement, T>);
      m_conclusions.emplace_back
        (std::make_unique<T>(std::forward<args_t>(args)...));
      return *this;
    }

    std::string_view m_name;
    std::vector<std::unique_ptr<Statement>> m_hypotheses;
    std::vector<std::unique_ptr<Statement>> m_conclusions;

    /** Converse of a theorem: swap hypotheses and conclusions.

        This is useful to avoid repetition here and there.
        It is a private method,
        because the converse of a correct theorem is often incorrect,
        and we want only correct theorems in the public API.
    */
    [[nodiscard]] Theorem converse(const std::string_view &name,
                     const std::string_view &newclid_rule) const;
    /** Rule identifier (usually, something like `r23`) in Newclid. */
    std::string_view m_newclid_rule;
  };

  std::ostream &operator<<(std::ostream &out, const Theorem &thm);
  void tag_invoke(boost::json::value_from_tag /*unused*/,
                  boost::json::value& jval, const Theorem& thm);

}
