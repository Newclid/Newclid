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
#include <optional>
#include "statement.hpp"
#include "typedef.hpp" // Assuming point, angle are defined here

namespace Yuclid {
  class EqualLineAngles;

  class EqualAngles : public Statement {
  public:
    EqualAngles(Angle a1, Angle a2);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::array<EqualAngles, 4> permutations() const;

    // Public read-only access methods
    [[nodiscard]] const Angle& left_angle() const { return m_left; }
    [[nodiscard]] const Angle& right_angle() const { return m_right; }
    auto operator<=>(const EqualAngles &other) const = default;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<EqualAngles>(*this);
    }

    [[nodiscard]] EqualLineAngles to_equal_line_angles() const;

    [[nodiscard]] bool is_refl() const override;

    std::ostream &print(std::ostream &out) const override;

    /**
     * @brief Export to json for Newclid
     *
     * Newclid's `equal_angles` expects 8 arguments, not 6.
     */
    [[nodiscard]] boost::json::object to_json() const override;

  protected:
    [[nodiscard]] std::optional<Equation<SlopeAngle>> as_equation_slope_angle() const override;

  private:
    Angle m_left;
    Angle m_right;
  };

} // namespace Yuclid    
