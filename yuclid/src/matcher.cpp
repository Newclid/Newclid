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
#include "matcher.hpp"

#include <boost/container_hash/hash.hpp>
#include <functional>
#include <cmath>
#include "numbers/add_circle.hpp"
#include "numbers/util.hpp"
#include "problem.hpp"
#include "statement/circumcenter.hpp"
#include "statement/coll.hpp"
#include "statement/angle_eq.hpp"
#include "statement/cyclic.hpp"
#include "statement/midpoint.hpp"
#include "statement/orthocenter.hpp"
#include "statement/para.hpp"
#include "statement/parallelogram.hpp"
#include "statement/perp.hpp"
#include "statement/similar_triangles.hpp"
#include "statement/congruent_triangles.hpp"
#include "statement/thales.hpp"
#include "theorem.hpp"
#include "type/sin_or_dist.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"
#include "config_options.hpp"

#include <algorithm>
#include <boost/log/trivial.hpp>
#include <cstddef>
#include <span>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>
#include <unordered_set>

using namespace std;


namespace Yuclid {

  namespace {
    template<class VectorType, class KeyFunType, class CallbackType>
    requires
      (is_invocable_r_v<double, KeyFunType, typename VectorType::value_type>
      || is_invocable_r_v<double, KeyFunType, const typename VectorType::value_type&>)
      && (is_invocable_r_v<void, CallbackType, span<typename VectorType::value_type>>
      || is_invocable_r_v<void, CallbackType, span<const typename VectorType::value_type>>)
    void foreach_bucket(VectorType& items,
                        KeyFunType key_fun,
                        const CallbackType& callback) {
      // Determine the element type of the span based on the constness of vector_type
      using ItemType = typename VectorType::value_type;
      using SpanElementType =
        conditional_t<is_const_v<remove_reference_t<VectorType>>,
                      const ItemType,
                      ItemType>;

      if (items.empty()) {
        return;
      }
      size_t start_bucket_index = 0;
      double start_bucket_key = invoke(key_fun, items[0]);
      double last_key = start_bucket_key;
      for (size_t ind = 1; ind < items.size(); ++ ind) {
        const double& key = invoke(key_fun, items[ind]);
        // If we stay in the same bucket, test if exceeded 10x tolerance
        // and update `last_key`
        if (key < last_key + EPS) {
          // If we went over 10x the tolerance by tiny steps, then issue a warning.
          if (key >= start_bucket_key + 10 * EPS) {
            BOOST_LOG_TRIVIAL(warning) << "While sorting " << typeid(ItemType).name()
                                       << ": bucket tolerance 10x overflow";
          }
        } else {
          // The new value does not belong to the current bucket.
          // Act on the current bucket and start the new one.
          callback(span<SpanElementType>(items).subspan(start_bucket_index,
                                                        ind - start_bucket_index));
          start_bucket_index = ind;
          start_bucket_key = key;
        }
        last_key = key;
      }
      callback(span<SpanElementType>(items).subspan(start_bucket_index));
    }

    template <typename value_type, typename callback_type>
    requires
      std::is_invocable_v<callback_type, const value_type&, const value_type&>
    void foreach_pair(const vector<pair<double, value_type>> &items,
                      callback_type callback) {
      foreach_bucket(items, &pair<double, value_type>::first,
                     [callback](span<const pair<double, value_type>> bucket) {
                       size_t const size = bucket.size();
                       for (size_t i = 0; i < size; ++ i) {
                         for (size_t j = i + 1; j < size; ++ j) {
                           callback(bucket[i].second, bucket[j].second);
                         }
                       }
                     });
    }
  }

  TheoremMatcher::TheoremMatcher(const Problem *prob, const Config::Solver *config) :
    m_problem(prob), m_config(config) {
    match_similar_triangles();
    match_between();
    auto important_angles = match_equal_angles();
    match_law_sin(important_angles);
    match_circles();
    match_parallelograms();
    if (m_config->ar_enabled<SquaredDist>() && m_config->eqn_statements_enabled()) {
      match_perpendiculars();
    } else {
      match_orthocenters();
    }
  }

  vector<tuple<double, double, Triangle>> TheoremMatcher::all_triangles() {
    vector<tuple<double, double, Triangle>> res;
    const size_t num_pts = m_problem->num_points();
    // If there are no isosceles triangles,
    // then the right estimate is `n * (n - 1) * (n - 2) / 6`.
    // We use a slightly larger number
    // to leave room for copies of isosceles triangles.
    res.reserve(num_pts * num_pts * num_pts / 6);
    for (const auto &pt_a : m_problem->all_points()) {
      for (const auto &pt_b : m_problem->all_points()) {
        if (pt_a.is_close(pt_b)) {
          continue;
        }
        for (const auto &pt_c : m_problem->all_points()) {
          if (Collinear(pt_a, pt_b, pt_c).check_equations()) {
            continue;
          }
          // In order to deduplicate triangles,
          // we only select those with `|AB| <= |BC| <= |AC|`,
          // leaving a room for error.
          double const dist_ab(Dist(pt_a, pt_b));
          double const dist_ac(Dist(pt_a, pt_c));
          double const dist_bc(Dist(pt_b, pt_c));
          if (dist_ab > (1 + REL_TOL) * dist_bc) {
            continue;
          }
          if (dist_bc > (1 + REL_TOL) * dist_ac) {
            continue;
          }
          res.emplace_back(dist_ab / dist_ac,
                           dist_ab / dist_bc,
                           Triangle(pt_a, pt_b, pt_c));
        }
      }
    }
    return res;
  }

  void TheoremMatcher::on_similar_triangles(const SimilarTriangles &simtri) {
    for (const auto& rotated : simtri.cyclic_rotations()) {
      insert_theorem(Theorem::similar_triangles_of_sas(rotated));
    }
    CongruentTriangles const congtri(simtri.left(),
                                     simtri.right(),
                                     simtri.same_clockwise());
    if (congtri.check_numerically()) {
      insert_theorem(Theorem::congruent_triangles_of_similar_triangles(congtri));
      insert_theorem(Theorem::congruent_triangles_properties(congtri));
    }
    insert_theorem(Theorem::similar_triangles_properties(simtri));
    insert_theorem(Theorem::similar_triangles_of_aa(simtri));
    insert_theorem(Theorem::similar_triangles_of_sss(simtri));
  }

  void TheoremMatcher::on_span_triangles(span<const tuple<double, double, Triangle>> bucket) {
    size_t const bucket_size = bucket.size();
    for (size_t left = 0; left < bucket_size; ++ left) {
      double const area_left = get<2>(bucket[left]).area();
      for (size_t right = left + 1; right < bucket_size; ++ right) {
        bool const same_clockwise = (area_left > 0) == (get<2>(bucket[right]).area() > 0);
        on_similar_triangles({
            get<2>(bucket[left]),
            get<2>(bucket[right]),
            same_clockwise
          });
      }
    }
  }

  void TheoremMatcher::match_similar_triangles() {
    using item_type = tuple<double, double, Triangle>;
    auto triangles = all_triangles();
    // Sort by `|AB|:|AC|`.
    ranges::sort(triangles, {}, [](const auto& item) {
      return std::get<0>(item);
    });
  
  
    foreach_bucket(triangles,
                   [](const auto& item) { return std::get<0>(item); },
                   [this](span<item_type> outer_bucket) {
                     ranges::sort(outer_bucket, {}, [](const auto& item) {
                       return std::get<1>(item);
                     });
                     foreach_bucket(outer_bucket, [](const auto& item) {
                       return std::get<1>(item);
                     }, [this](span<const item_type> bucket) {
                       on_span_triangles(bucket);
                     });
                   });
  }

  void TheoremMatcher::insert_theorem(const Theorem &thm) {
    if (!thm.check_numerically()) {
      return;
    }
    m_theorems.push_back(thm.normalize());
  }

  vector<pair<double, Collinear>> TheoremMatcher::sorted_between() {
    vector<pair<double, Collinear>> all_between;
    for (auto right : m_problem->all_points()) {
      for (auto middle : m_problem->all_points()) {
        for (auto left : right.up_to()) {
          Collinear const pred(left, middle, right);
          if (!pred.check_numerically() || !pred.is_between()) {
            continue;
          }
          on_between({left, middle, right});
          double const dist_left(Dist(left, middle));
          double const dist_right(Dist(middle, right));
          if (dist_left <= (1 + REL_TOL) * dist_right) {
            all_between.emplace_back(dist_left / (dist_left + dist_right),
                                     pred);
            if (dist_right <= (1 + REL_TOL) * dist_left) {
              on_midpoint({left, middle, right});
            }
          }
          if (dist_right <= (1 + REL_TOL) * dist_left) {
            all_between.emplace_back(dist_right / (dist_right + dist_left),
                                     Collinear(right, middle, left));
          }
        }
      }
    }
    ranges::sort(all_between, {}, &pair<double, Collinear>::first);
    return all_between;
  }

  void TheoremMatcher::on_between(const Collinear& pred) {
    if (m_config->ar_enabled<Dist>() && m_config->eqn_statements_enabled()) {
      insert_theorem(Theorem::coll_of_add_length(pred));
      insert_theorem(Theorem::add_length_of_between(pred));
    }
    for (const auto &perm : pred.cyclic_permutations()) {
      insert_theorem(Theorem::coll_of_para(perm));
      insert_theorem(Theorem::para_of_coll(perm));
    }
  }

  void TheoremMatcher::on_midpoint(const Midpoint& pred) {
    if (m_config->ar_enabled<SquaredDist>() && m_config->eqn_statements_enabled()) {
      for (const auto &other : m_problem->all_points()) {
        if (other == pred.left() || other == pred.middle() || other == pred.right()) {
          continue;
        }
        insert_theorem(Theorem::sum_squares_of_midpoint(pred, other));
      }
    }
    if (!m_config->ar_enabled<Dist>()) {
      insert_theorem(Theorem::midpoint_ratio_dist(pred));
    }
    if (!m_config->eqn_statements_enabled()) {
      for (const auto &other : m_problem->all_points()) {
        if (other == pred.left() || other == pred.middle() || other == pred.right()) {
          continue;
        }
        if (Perpendicular(SlopeAngle(pred.left(), other),
                          SlopeAngle(other, pred.right())).check_numerically()) {
          insert_theorem(Theorem::hypotenuse_is_diameter(pred, other));
        }
      }
    }
    insert_theorem(Theorem::midpoint_of_coll_cong(pred));
    insert_theorem(Theorem::coll_of_midpoint(pred));
    insert_theorem(Theorem::cong_of_midpoint(pred));
  }

  void TheoremMatcher::match_between() {
    const vector<pair<double, Collinear>> all = sorted_between();
    foreach_pair(all, [this](const Collinear& left, const Collinear& right) {
      on_between_equal_ratio(left, right);
    });
  }

  void TheoremMatcher::on_between_equal_ratio(const Collinear &left,
                                              const Collinear &right) {
    insert_theorem(Theorem::rotate_equal_ratio_of_same_side(left, right));
    insert_theorem(Theorem::rotate_equal_ratio_of_same_side
                   (Collinear(left.b(), left.c(), left.a()),
                    Collinear(right.b(), right.c(), right.a())));
    insert_theorem(Theorem::rotate_equal_ratio_of_same_side
                   (Collinear(left.c(), left.a(), left.b()),
                    Collinear(right.c(), right.a(), right.b())));
    if (left.a() == right.a() || left.b() == right.b() || left.c() == right.c()) {
      return;
    }
    Thales const thales(left, right);
    if (!thales.check_numerically()) {
      return;
    }
    insert_theorem(Theorem::thales_para_of_eqratio(thales));
    insert_theorem(Theorem::thales_para_of_eqratio(thales.rotate()));
    insert_theorem(Theorem::thales_para_of_eqratio(thales.rotate().rotate()));
    insert_theorem(Theorem::thales_eqratio_of_para(thales));
  }

  vector<pair<double, Angle>> TheoremMatcher::all_angles() {
    // Create buckets of approximately equal angles.
    size_t const num_pts = m_problem->num_points();
    vector<pair<double, Angle>> all;
    all.reserve(num_pts * (num_pts - 1) * (num_pts - 2));
    for (const Point &left : m_problem->all_points()) {
      for (const Point &vertex : m_problem->all_points()) {
        for (const Point &right : m_problem->all_points()) {
          if (!Collinear(left, vertex, right).check_equations()) {
            Angle ang {left, vertex, right};
            all.emplace_back(AddCircle<double>(ang).number(), ang);
          }
        }
      }
    }
    ranges::sort(all, {}, &pair<double, Angle>::first);
    return all;
  }

  unordered_set<SinOrDist, boost::hash<SinOrDist>> TheoremMatcher::match_equal_angles() {
    const vector<pair<double, Angle>> all = all_angles();
    unordered_set<SinOrDist, boost::hash<SinOrDist>> important_angles;

    // Process pairs of equal angles
    // and note the angles that are equal to other angles.
    auto const process_bucket =
      [this, &important_angles](span<const pair<double, Angle>> bucket) {
        size_t const size = bucket.size();
        for (size_t left = 0; left < size; ++ left) {
          important_angles.insert(SinOrDist(bucket[left].second));
          for (size_t right = left + 1; right < size; ++ right) {
            on_equal_angles(bucket[left].second, bucket[right].second);
          }
        }
      };

    foreach_bucket(all, &pair<double, Angle>::first, process_bucket);
    if (m_config->ar_enabled<SquaredDist>() && m_config->eqn_statements_enabled()) {
      for (const auto &item :
             ranges::equal_range(all,
                                 rat2double(Rat(1, 2)),
                                 [](double left, double right) { return left < right - EPS; },
                                 &pair<double, Angle>::first)) {
        insert_theorem(Theorem::pythagoras_of_perp(item.second));
        insert_theorem(Theorem::pythagoras_of_sum_squares(item.second));
      }
    }

    // Add theorems like `\sin² ABC = 1/4 ↔ ∠ABC = π / 6`
    if (m_config->eqn_statements_enabled() && m_config->ar_sin_enabled()) {
      const auto sin_squares = known_sin_squares();
      for (size_t i = 0; i < sin_squares.size(); ++ i) {
        for (const auto &[ang_val, ang] :
               ranges::equal_range(all,
                                   rat2double(sin_squares[i].first),
                                   [](double left, double right) { return left < right - EPS; },
                                   &pair<double, Angle>::first)) {
          insert_theorem(Theorem::sin_eq_of_angle_eq(ang, i));
          insert_theorem(Theorem::angle_eq_of_sin_eq(ang, i));
        }
      }
    }

    return important_angles;
  }

  void TheoremMatcher::on_equal_angles(const Angle& left, const Angle& right) {
    // If the equality has a form `∠ ABD = ∠ ACD`,
    // then it's a cyclic quadrilateral `ABCD`.
    // In order to avoid duplicate matches,
    // we only match if `B, C < A < D`.
    // This way we match each quadrilateral once.
    if (left.left() == right.left()
        && left.right() == right.right()
        && left.left() < left.right()
        && left.vertex() < left.left()
        && right.vertex() < right.left()) {
      on_cyclic({left.vertex(), right.vertex(), left.left(), left.right()});
    }

    // Process `∠ ABC = ∠ CBD`, `A ≠ D`.
    // Without deduplication, each bisector is matched twice,
    // once as `∠ ABC = ∠ CBD` (or `∠ CBD = ∠ ABC`)
    // and once as `∠ CBA = ∠ DBC` (or `∠ DBC = ∠ CBA`).
    //
    // In order to deduplicate these,
    // we require that `A < D` in terms of indexes.
    if (left.vertex() == right.vertex()) {
      if (left.right() == right.left()
          && left.left() < right.right()) {
        on_point_on_bisector(left.right(), {left.left(), left.vertex(), right.right()});
      } else if (left.left() == right.right()
                 && right.left() < left.right()) {
        on_point_on_bisector(left.left(), {right.left(), left.vertex(), left.right()});
      }
    }

    // Match `α = β ↔ \sin² α = \sin² β`.
    // Formally, `\sin² α = \sin² β` implies `α = ±β`,
    // but we choose the right sign by numerical checks.
    // We exclude right angles,
    // because we would get `\sin² ∠ABC = \sin² ∠CBA` by reflexivity,
    // then would get `∠ABC = ∠CBA` (hence `AB ⟂ BC`) for free.
    //
    // In the future, we should add explicit assumptions
    // to `equal_angles_of_sin_eq_sin`.
    if (m_config->ar_sin_enabled() && m_config->eqn_statements_enabled()) {
      if (SinOrDist(left) != SinOrDist(right)) {
        insert_theorem(Theorem::sin_eq_sin_of_equal_angles({left, right}));
      }
      if (!Perpendicular(SlopeAngle(left.vertex(), left.left()),
                         SlopeAngle(left.vertex(), left.right()))
          .check_equations()) {
        insert_theorem(Theorem::equal_angles_of_sin_eq_sin({left, right}));
      }
    } // if ar_sin_enabled
  }

  void TheoremMatcher::on_cyclic(const CyclicQuadrangle& pred) {
    insert_theorem(Theorem::cyclic_of_equal_angles(pred));
    insert_theorem(Theorem::cyclic_of_equal_angles({pred.a(), pred.c(), pred.b(), pred.d()}));
    insert_theorem(Theorem::cyclic_of_equal_angles({pred.b(), pred.c(), pred.a(), pred.d()}));
    insert_theorem(Theorem::cyclic_properties(pred));
    if (Parallel(SlopeAngle(pred.a(), pred.b()),
                 SlopeAngle(pred.c(), pred.d())).check_equations()) {
      on_isosceles_trapezoid(pred.c(), pred.a(), pred.b(), pred.d());
    }
    if (Parallel(SlopeAngle(pred.a(), pred.c()),
                 SlopeAngle(pred.b(), pred.d())).check_equations()) {
      on_isosceles_trapezoid(pred.b(), pred.a(), pred.c(), pred.d());
    }
    if (Parallel(SlopeAngle(pred.a(), pred.d()),
                 SlopeAngle(pred.b(), pred.c())).check_equations()) {
      on_isosceles_trapezoid(pred.a(), pred.b(), pred.c(), pred.d());
    }
  }

  void TheoremMatcher::on_isosceles_trapezoid(const Point& pt_a,
                                              const Point& pt_b,
                                              const Point& pt_c,
                                              const Point& pt_d) {
    insert_theorem(Theorem::equal_angles_of_cong_cyclic(pt_a, pt_b, pt_c, pt_d));
    insert_theorem(Theorem::equal_angles_of_cong_cyclic(pt_a, pt_c, pt_b, pt_d));
    insert_theorem(Theorem::equal_angles_of_iso_trapezoid(pt_a, pt_b, pt_c, pt_d));
    insert_theorem(Theorem::equal_angles_of_iso_trapezoid(pt_a, pt_c, pt_b, pt_d));
  }

  void TheoremMatcher::on_point_on_bisector(const Point& point, const Angle& angle) {
    insert_theorem(Theorem::angle_bisector_meets_bisector(angle, point));
    if (!m_config->ar_sin_enabled() || !m_config->eqn_statements_enabled()) {
      insert_theorem(Theorem::triangle_bisector_of_equal_angles(point, angle));
      insert_theorem(Theorem::triangle_bisector_of_eqratio(point, angle));
    }
    insert_theorem(Theorem::incenter(point, angle));
  }

  void TheoremMatcher::match_circles() {
    const size_t num_pts = m_problem->num_points();
    for (const Point &center : m_problem->all_points()) {
      vector<pair<double, Point>> pts;
      pts.reserve(num_pts - 1);
      for (const Point &other : m_problem->all_points()) {
        if (!center.is_close(other)) {
          pts.emplace_back(double(Dist(center, other)), other);
        }
      }
      ranges::sort(pts, {}, &pair<double, Point>::first);
      foreach_bucket(pts, &pair<double, Point>::first,
                     [&center, this](span<const pair<double, Point>> bucket) {
                       on_circle(center, bucket);
                     });
    }
  }

  void TheoremMatcher::on_circle(const Point &center, span<const pair<double, Point>> points) {
    size_t const size = points.size();
    for (size_t pt_a = 0; pt_a < size; ++ pt_a) {
      for (size_t pt_b = pt_a + 1; pt_b < size; ++ pt_b) {
        on_isosceles_triangle(center, points[pt_a].second, points[pt_b].second);
        for (size_t pt_c = pt_b + 1; pt_c < size; ++ pt_c) {
          on_circumcenter({
              center, {points[pt_a].second, points[pt_b].second, points[pt_c].second}
            });
          for (size_t pt_d = pt_c + 1; pt_d < size; ++ pt_d) {
            on_quadrangle_circumcenter(center,
                                       { points[pt_a].second, points[pt_b].second,
                                         points[pt_c].second, points[pt_d].second });
          }
        }
      }
    }
  }

  void TheoremMatcher::on_isosceles_triangle(const Point &vertex,
                                             const Point &left,
                                             const Point &right) {
    if (Collinear(vertex, left, right).check_equations()) {
      return;
    }
    insert_theorem(Theorem::equal_angles_of_cong(vertex, left, right));
    insert_theorem(Theorem::cong_of_equal_angles(vertex, left, right));
  }

  void TheoremMatcher::on_circumcenter(const Circumcenter &pred) {
    if (m_config->eqn_statements_enabled()) {
      insert_theorem(Theorem::arc_of_circumcenter(pred));
      for (const auto &tri : pred.triangle().cyclic_rotations()) {
        insert_theorem(Theorem::circumcenter_of_arc({pred.center(), tri}));
      }
    }
    insert_theorem(Theorem::circumcenter_of_cong(pred));
    insert_theorem(Theorem::cong_of_circumcenter(pred));
  }

  void TheoremMatcher::on_quadrangle_circumcenter(const Point& center,
                                                  const CyclicQuadrangle& cyc) {
    // This theorem can be proved by other means,
    // if eqns are allowed in statements.
    if (!m_config->eqn_statements_enabled()) {
      insert_theorem(Theorem::cong_of_circumcenter_of_cyclic
                     ({center, Triangle(cyc.a(), cyc.b(), cyc.c())}, cyc.d()));
      insert_theorem(Theorem::cong_of_circumcenter_of_cyclic
                     ({center, Triangle(cyc.b(), cyc.c(), cyc.d())}, cyc.a()));
      insert_theorem(Theorem::cong_of_circumcenter_of_cyclic
                     ({center, Triangle(cyc.c(), cyc.d(), cyc.a())}, cyc.b()));
      insert_theorem(Theorem::cong_of_circumcenter_of_cyclic
                     ({center, Triangle(cyc.d(), cyc.a(), cyc.b())}, cyc.c()));
    }
    insert_theorem(Theorem::center_of_cyclic_of_cong_of_cong(cyc, center));
    insert_theorem(Theorem::center_of_cyclic_of_cong_of_cong({
          cyc.a(), cyc.c(), cyc.b(), cyc.d()
        }, center));
    insert_theorem(Theorem::center_of_cyclic_of_cong_of_cong({
          cyc.a(), cyc.d(), cyc.b(), cyc.c()
        }, center));
  }


  void TheoremMatcher::match_parallelograms() {
    if (m_config->ar_enabled<SquaredDist>() && m_config->eqn_statements_enabled()) {
      for (const auto &pt_d : m_problem->all_points()) {
        for (const auto &pt_c : pt_d.up_to()) {
          for (const auto &pt_a : pt_c.up_to()) {
            for (const auto &pt_b : m_problem->all_points()) {
              if (pt_a == pt_b || pt_b == pt_c || pt_b == pt_d) {
                continue;
              }
              Parallelogram const pred(pt_a, pt_b, pt_c, pt_d);
              insert_theorem(Theorem::parallelogram_law(pred));
            }
          }
        }
      }
    }
  }

  void TheoremMatcher::match_perpendiculars() {
    for (const auto &pt_b : m_problem->all_points()) {
      for (const auto &pt_a : pt_b.up_to()) {
        for (const auto &pt_d : pt_b.up_to()) {
          for (const auto &pt_c : pt_d.up_to()) {
            if (pt_a == pt_c || pt_a == pt_d) {
              continue;
            }
            Perpendicular const pred(SlopeAngle(pt_a, pt_b), SlopeAngle(pt_c, pt_d));
            if (pred.check_equations()) {
              insert_theorem(Theorem::perp_of_sum_squares(pred));
              insert_theorem(Theorem::sum_squares_of_perp(pred));
            }
          }
        }
      }
    }
  }

  void TheoremMatcher::match_orthocenters() {
    for (const auto &pt_d : m_problem->all_points()) {
      for (const auto &pt_c : pt_d.up_to()) {
        for (const auto &pt_b : pt_c.up_to()) {
          for (const auto &pt_a : pt_b.up_to()) {
            IsOrthocenter const pred(Triangle{pt_a, pt_b, pt_c}, pt_d);
            if (pred.check_numerically()) {
              insert_theorem(Theorem::orthocenter(pred));
              insert_theorem(Theorem::orthocenter({Triangle{pt_b, pt_c, pt_a}, pt_d}));
              insert_theorem(Theorem::orthocenter({Triangle{pt_c, pt_a, pt_b}, pt_d}));
            }
          }
        }
      }
    }
  }

  void TheoremMatcher::match_law_sin(const unordered_set<SinOrDist, boost::hash<SinOrDist>> &angles) {
    if (m_config->ar_sin_enabled() && m_config->eqn_statements_enabled()) {
      for (const Point &pt_c : m_problem->all_points()) {
        for (const Point &pt_b : pt_c.up_to()) {
          for (const Point &pt_a : pt_b.up_to()) {
            if (!Collinear(pt_a, pt_b, pt_c).check_equations()) {
              Triangle tri {pt_a, pt_b, pt_c};
              bool const sin_a = angles.contains(SinOrDist(tri.angle_a()));
              bool const sin_b = angles.contains(SinOrDist(tri.angle_b()));
              bool const sin_c = angles.contains(SinOrDist(tri.angle_c()));
              if (sin_a && sin_b) {
                insert_theorem(Theorem::law_of_sines(tri));
              }
              if (sin_b && sin_c) {
                insert_theorem(Theorem::law_of_sines({tri.b(), tri.c(), tri.a()}));
              }
              if (sin_a && !sin_b && sin_c) {
                insert_theorem(Theorem::law_of_sines({tri.c(), tri.a(), tri.b()}));
              }
            }
          }
        }
      }
    }
  }

}
