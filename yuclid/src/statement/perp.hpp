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
#include <variant>
#include <optional>
#include "statement.hpp"
#include "typedef.hpp"

namespace Yuclid {

  class Perpendicular : public Statement {
  public:
    Perpendicular(SlopeAngle s1, SlopeAngle s2);
    Perpendicular() = delete;

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const SlopeAngle& left() const { return m_left; }
    [[nodiscard]] const SlopeAngle& right() const { return m_right; }

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<Perpendicular>(*this);
    }

    std::ostream &print(std::ostream &out) const override;
    [[nodiscard]] Perpendicular swap() const;

  protected:
    [[nodiscard]] std::optional<Equation<SlopeAngle>> as_equation_slope_angle() const override;
  private:
    SlopeAngle m_left;
    SlopeAngle m_right;
  };

} // namespace Yuclid
