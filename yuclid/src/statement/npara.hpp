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
#include "typedef.hpp" // Assuming point is defined here

namespace Yuclid {

  class NonParallel : public Statement {
  public:
    NonParallel(const SlopeAngle &left, const SlopeAngle &right) :
      m_left(left), m_right(right) { }

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] bool check_equations() const override { return true; }
    [[nodiscard]] bool numerical_only() const override { return true; }

    // Public read-only access methods
    [[nodiscard]] const SlopeAngle &left() const { return m_left; }
    [[nodiscard]] const SlopeAngle &right() const { return m_right; }

    auto operator<=>(const NonParallel &other) const = default;

    std::ostream &print(std::ostream &out) const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<NonParallel>(*this);
    }

    ~NonParallel() override = default;

  private:
    SlopeAngle m_left, m_right;
  };

} // namespace Yuclid
