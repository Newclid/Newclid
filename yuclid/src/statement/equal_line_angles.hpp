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
#include "typedef.hpp" // Assuming point, angle are defined here

namespace Yuclid {

  /**
   * @brief Equality of oriented angles between lines
   *
   * This statement says that two angles between lines are equal.
   * While we never use this statement in theorems
   * (thus we can only prove it via AR),
   * it is useful to state some problems.
   *
   * Also, it is here for backward compatibility with Alpha Geometry
   * and Newclid.
   */
  class EqualLineAngles : public Statement {
  public:
    EqualLineAngles(SlopeAngle left_left, SlopeAngle left_right,
                      SlopeAngle right_left, SlopeAngle right_right);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const SlopeAngle& left_left() const { return m_left_left; }
    [[nodiscard]] const SlopeAngle& left_right() const { return m_left_right; }
    [[nodiscard]] const SlopeAngle& right_left() const { return m_right_left; }
    [[nodiscard]] const SlopeAngle& right_right() const { return m_right_right; }
    auto operator<=>(const EqualLineAngles &other) const = default;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<EqualLineAngles>(*this);
    }

    [[nodiscard]] bool is_refl() const override;

    std::ostream &print(std::ostream &out) const override;

  protected:
    [[nodiscard]] std::optional<Equation<SlopeAngle>> as_equation_slope_angle() const override;
  private:
    /** Sides of the line angles. */
    SlopeAngle m_left_left, m_left_right, m_right_left, m_right_right;
  };

} // namespace Yuclid    
