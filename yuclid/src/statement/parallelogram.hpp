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
#include <memory>
#include <string>
#include <vector>
#include "statement.hpp"
#include "typedef.hpp"

namespace Yuclid {
  class DistEqDist;
  class Parallel;
  template<typename t>
  class EqnStatement;

  class Parallelogram : public Statement {
  public:
    Parallelogram(const Point &a, const Point &b, const Point &c, const Point &d);
    Parallelogram(const std::vector<statement_arg> &args);

    [[nodiscard]] std::string name() const override;

    [[nodiscard]] std::array<Parallelogram, 8> permutations() const;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;

    [[nodiscard]] bool check_nondegen() const override;

    [[nodiscard]] bool check_equations() const override;

    [[nodiscard]] std::vector<statement_arg> args() const override;
    auto operator<=>(const Parallelogram &other) const = default;

    [[nodiscard]] Parallel para_ab_cd() const;
    [[nodiscard]] Parallel para_ad_bc() const;
    [[nodiscard]] DistEqDist cong_ab_cd() const;
    [[nodiscard]] DistEqDist cong_ad_bc() const;
    [[nodiscard]] EqnStatement<SquaredDist> parallelogram_law_eqn() const;

    [[nodiscard]] const Point &a() const { return m_a; }
    [[nodiscard]] const Point &b() const { return m_b; }
    [[nodiscard]] const Point &c() const { return m_c; }
    [[nodiscard]] const Point &d() const { return m_d; }

    [[nodiscard]] std::vector<Point> points() const override;

    std::ostream &print(std::ostream &out) const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<Parallelogram>(*this);
    }

    ~Parallelogram() override = default;
  private:
    Point m_a, m_b, m_c, m_d;
  };

} // namespace Yuclid
