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
#include "statement/statement.hpp"
#include "ratio_squared_dist.hpp"
#include "type/point.hpp"
#include <boost/json/conversion.hpp>
#include <boost/json/object.hpp>
#include <boost/json/value.hpp>
#include <boost/json/value_from.hpp>
#include <memory>
#include <optional>
#include <ostream>
#include <ranges>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {
  bool Statement::is_refl() const {
    return false;
  }

  optional<RatioSquaredDist> Statement::as_ratio_squared_dist() const {
    return nullopt;
  }

  bool Statement::numerical_only() const {
    return false;
  }

  ostream &Statement::print_newclid(ostream & /*unused*/) const {
    throw runtime_error(string("`print_newclid()` is not implemented for ") + name());
  }

  ostream &operator<<(ostream &out, const Statement &p) {
    return p.print(out);
  }

  boost::json::object Statement::to_json() const {
    std::vector<Point> v = points() | ranges::to<vector>();
    return {
      {"name", name()},
      {"points", boost::json::value_from(v)}
    };
  }

}

namespace std {

  /** `tag_invoke` for `std::unique_ptr<Statement>`.
   *
   * It must live in `std::` namespace
   */
  void tag_invoke(boost::json::value_from_tag /*unused*/, boost::json::value& jv,
                  const unique_ptr<Yuclid::Statement>& p) {
    jv = p->to_json();
  }

}
