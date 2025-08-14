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
#include <boost/container_hash/hash.hpp>
#include <vector>
#include <span>
#include <tuple>
#include <unordered_set>

#include "config_options.hpp"

namespace Yuclid {
  class Angle;
  class Circumcenter;
  class Collinear;
  class CyclicQuadrangle;
  class Midpoint;
  class Point;
  class Problem;
  class SimilarTriangles;
  class SinOrDist;
  class Theorem;
  class Triangle;

  class TheoremMatcher {
  public:
    explicit TheoremMatcher(const Problem *prob, const Config::Solver *config);
    [[nodiscard]] const std::vector<Theorem> &theorems() const {
      return m_theorems;
    }
  private:
    /**
     * @brief Numerically check the theorem, then record it as a match.
     *
     * If both hypotheses and conclusions of `thm` are true numerically,
     * append its normalized version to `m_theorems`.
     */
    void insert_theorem(const Theorem &thm);
    /**
     * @brief Match theorems about similar triangles.
     *
     * Find numerically sound statements `▵ABC ∼ ▵DEF` and `▵ABC ∼r ▵DEF`,
     * and add theorems about these statements.
     */
    void match_similar_triangles();

    /**
     * @brief Generate all triangles with `|AB| ≤ (1 + ε)|BC| ≤ (1 + ε)²|AC|`.
     *
     * This function returns an `std::vector`
     * of tuples `(|AB| / |AC|, |AB| / |BC|, ▵ABC)`
     * over all triangles with `|AB| ≤ (1 + ε)|BC| ≤ (1 + ε)²|AC|`,
     * where `ε = REL_TOL`.
     *
     * The tuples aren't sorted.
     */
    std::vector<std::tuple<double, double, Triangle>> all_triangles();

    /**
     * @brief Add theorems about a pair of similar triangles.
     *
     * @param simtri A pair of numerically similar triangles.
     */
    void on_similar_triangles(const SimilarTriangles& simtri);

    /**
     * @brief Process a span of pairwise similar triangles.
     *
     * @param bucket An `std::span` of triangles that are pairwise similar.
     */
    void on_span_triangles(std::span<const std::tuple<double, double, Triangle>> bucket);

    /**
     * @brief Generate all triples of points `(A, B, C)`
     * with `B` between `A` and `C`, `AB ≤ (1 + ε) BC`.
     *
     * The triples are sorted by `|AB|:|AC|`.
     * If `|AB| ≈ |BC|`, then both `(A, B, C)` and `(C, B, A)` are returned.
     *
     * Also inserts theorems about individual triples `(A, B, C)`.
     */
    std::vector<std::pair<double, Collinear>> sorted_between();

    /**
     * @brief Add theorems about a single triple of points `(A, B, C)`,
     * where `B` is between `A` and `C`.
     *
     * Should be called once for each triple `(A, B, C)`,
     * and only for one of `(A, B, C)` and `(C, B, A)`.
     */
    void on_between(const Collinear &pred);

    /**
     * @brief Add theorems about 2 pairs of collinear triples with the same ratio.
     */
    void on_between_equal_ratio(const Collinear &left,
                                const Collinear &right);

    /**
     * @brief Add theorems about a `Midpoint`.
     */
    void on_midpoint(const Midpoint &pred);

    /**
     * @brief Run theorem matchers based on "between" triples.
     */
    void match_between();

    /**
     * @brief Match theorems based on equality of angles.
     */
    std::unordered_set<SinOrDist, boost::hash<SinOrDist>> match_equal_angles();

    std::vector<std::pair<double, Angle>> all_angles();

    void on_equal_angles(const Angle &left, const Angle &right);

    void on_cyclic(const CyclicQuadrangle &pred);

    /**
     * @brief Add theorems about an isosceles trapezoid.
     *
     * Given `A`, `B`, `C, `D` such that `AB = CD`, `BC ∥ AD`,
     * add theorems about `ABCD`.
     */
    void on_isosceles_trapezoid(const Point &pt_a, const Point &pt_b,
                                const Point &pt_c, const Point &pt_d);

    void on_point_on_bisector(const Point &point, const Angle &angle);

    void match_law_sin(const std::unordered_set<SinOrDist, boost::hash<SinOrDist>> &angles);

    void match_circles();

    void on_circle(const Point &center,
                   std::span<const std::pair<double, Point>> points);

    void on_isosceles_triangle(const Point &vertex,
                               const Point &left,
                               const Point &right);

    void on_circumcenter(const Circumcenter &pred);

    void on_quadrangle_circumcenter(const Point &center, const CyclicQuadrangle &cyc);

    void match_parallelograms();

    void match_perpendiculars();

    void match_orthocenters();

    const Problem *m_problem;
    const Config::Solver *m_config;

    std::vector<Theorem> m_theorems;
  };
}
