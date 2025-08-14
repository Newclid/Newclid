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
#include "coll.hpp"
#include <ranges>
#include <vector>

namespace Yuclid {
  class Parallel;

  class Thales : public Statement {
  public:
    Thales(const Collinear& b1, const Collinear& b2);

    // Explicit constructor from vector<statement_arg>
    explicit Thales(const std::vector<statement_arg>& args);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;

    [[nodiscard]] auto permutations() const {
#if HAVE_ZIP_TRANSFORM
      return 
        std::views::zip_transform([](const Collinear &left, const Collinear &right) -> Thales {
          return {left, right};
        }, m_left.permutations(), m_right.permutations());
#else
      return
        std::views::zip(m_left.permutations(), m_right.permutations())
        | std::views::transform([](const auto &arg) -> Thales {
          return {std::get<0>(arg), std::get<1>(arg)};
        });
#endif
    }

    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override;

    [[nodiscard]] Parallel para_ab() const;
    [[nodiscard]] Parallel para_ac() const;
    [[nodiscard]] Parallel para_bc() const;
    [[nodiscard]] Collinear coll_left() const;
    [[nodiscard]] Collinear coll_right() const;

    [[nodiscard]] Thales rotate() const;

    std::ostream &print(std::ostream &out) const override;

    // Defaulted three-way comparison operator
    auto operator<=>(const Thales &other) const = default;
  private:
    Collinear m_left;
    Collinear m_right;
  };

} // namespace Yuclid
