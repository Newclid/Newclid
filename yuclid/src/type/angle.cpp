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
#include "angle.hpp"
#include "numbers/add_circle.hpp"
#include "statement/ncoll.hpp"
#include "type/point.hpp"
#include "type/slope_angle.hpp"
#include "problem.hpp"
#include <cstddef>
#include <string>    // For std::string (used by point::name())
#include <iostream>  // For std::ostream
#include <stdexcept> // For std::runtime_error
#include <boost/container_hash/hash.hpp>

using namespace std;

namespace Yuclid {

  Angle::Angle(Point left_pt, Point vertex_pt, Point right_pt)
    : m_left_pt(left_pt),
      m_vertex_pt(vertex_pt),
      m_right_pt(right_pt)
  {
    // Check if the vertex is too close to the left point
    if (m_vertex_pt == m_left_pt || m_vertex_pt == m_right_pt) {
      string const error_msg = "Error: Cannot create angle " +
        m_left_pt.name() + " " + m_vertex_pt.name() + " " +
        m_right_pt.name() + ": equal points";
      throw std::runtime_error(error_msg);
    }
  }

  bool Angle::check_nondegen() const {
    return
      !m_vertex_pt.is_close(m_left_pt) &&
      !m_vertex_pt.is_close(m_right_pt);
  }

  SlopeAngle Angle::left_side() const {
    return {m_vertex_pt, m_left_pt};
  }

  SlopeAngle Angle::right_side() const {
    return {m_vertex_pt, m_right_pt};
  }

  Angle::operator AddCircle<double>() const {
    return AddCircle<double>(right_side()) - AddCircle<double>(left_side());
  }

  double Angle::dot_product() const {
    return ((m_left_pt.x() - m_vertex_pt.x()) * (m_right_pt.x() - m_vertex_pt.x())) +
      ((m_left_pt.y() - m_vertex_pt.y()) * (m_right_pt.y() - m_vertex_pt.y()));
  }

  size_t hash_value(const Angle& arg) {
    size_t seed = 0;
    boost::hash_combine(seed, arg.left());
    boost::hash_combine(seed, arg.vertex());
    boost::hash_combine(seed, arg.right());
    return seed;
  }

  std::ostream &operator<<(std::ostream &os, const Angle &ang) {
    os << "∠(" << ang.left() << " " << ang.vertex() << " " << ang.right() << ")";
    return os;
  }

} // namespace Yuclid
