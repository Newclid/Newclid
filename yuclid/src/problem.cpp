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
#include "problem.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"     // To create point objects for the map
#include "typedef.hpp"
#include <cstddef>
#include <memory>
#include <stdexcept>     // For std::out_of_range exception

#include <boost/log/trivial.hpp>
#include <string>
#include <utility>
#include <vector>

using namespace std;

namespace Yuclid {

  Point Problem::add_point(const string &name, double x, double y) {
    Point res(m_points.size(), this);
    m_points.emplace_back(name, x, y);
    return res;
  }

  const string& Problem::point_name(Point pt) const {
    return m_points.at(pt.get()).name();
  }

  void Problem::set_name(const std::string &name) {
    m_name = name;
  }

  void Problem::add_hypothesis(std::unique_ptr<Statement> &&p) {
    m_hypotheses.push_back(std::move(p));
  }

  const std::vector<std::unique_ptr<Statement>>& Problem::hypotheses() const {
    return m_hypotheses;
  }

  void Problem::add_goal(std::unique_ptr<Statement> &&p) {
    m_goals.push_back(std::move(p));
  }

  const std::vector<std::unique_ptr<Statement>>& Problem::goals() const {
    return m_goals;
  }

  double Problem::get_x(Point pt) const {
    return m_points.at(pt.get()).x();
  }

  double Problem::get_y(Point pt) const {
    return m_points.at(pt.get()).y();
  }

  size_t Problem::num_points() const {
    return m_points.size();
  }

  Point Problem::find_point(const string &name) const {
    const auto size = m_points.size();
    for (size_t ind = 0; ind < size; ++ ind) {
      if (m_points[ind].name() == name) {
        return {ind, this};
      }
    }
    throw runtime_error(format("Point named {} not found in the problem", name));
  }

} // namespace Yuclid
