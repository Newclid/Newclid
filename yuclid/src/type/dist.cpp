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
#include "dist.hpp"
#include "squared_dist.hpp" // Needed for explicit conversion to squared_dist
#include "sin_or_dist.hpp"
#include "type/point.hpp"
#include <algorithm> // For std::min and std::max
#include <cmath>     // For std::sqrt
#include <cstddef>
#include <ostream>
#include <boost/container_hash/hash.hpp>

using namespace std;

namespace Yuclid {

  Dist::Dist(Point p1, Point p2)
    : m_left(std::min(p1, p2)), // Assign the smaller-indexed point to m_left
      m_right(std::max(p1, p2)) // Assign the larger-indexed point to m_right
  {
    // The member initializers ensure m_left <= m_right based on point's operator<=>
  }

  Dist::operator double() const {
    // Create a temporary squared_dist object to get the squared value, then take its square root.
    // This implicitly uses the operator double() of squared_dist.
    return sqrt(static_cast<double>(SquaredDist(*this)));
  }

  Dist::operator SquaredDist() const {
    // Delegate to the squared_dist constructor, passing the two points.
    return {m_left, m_right};
  }

  Dist::operator SinOrDist() const {
    return SinOrDist(SquaredDist(*this));
  }

  std::ostream &operator<<(std::ostream &os, const Dist &d) {
    // Assuming point::name() returns std::string, direct streaming is possible.
    os << "|" << d.left().name() << "-" << d.right().name() << "|";
    return os;
  }

  size_t hash_value(const Dist& arg) {
    size_t seed = 0;
    boost::hash_combine(seed, arg.left());
    boost::hash_combine(seed, arg.right());
    return seed;
  }

} // namespace Yuclid
