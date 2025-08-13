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

#include "statement/statement.hpp"
#include <string>
#include <vector>

namespace Yuclid {
  class Angle;
  class Collinear;

  /**
   * @brief Represents that the angle `ABC` is obtuse.
   *
   * In particular, if `A`, `B`, `C` are collinear,
   * then this statement means that `B` is between `A` and `C`.
   */
  class ObtuseAngle : public Statement {
  public:
    ObtuseAngle(const Angle &ang);
    ObtuseAngle(const Collinear &arg);
    explicit ObtuseAngle(const std::vector<statement_arg>& args);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;

    /**
     * @brief Normalize a `obtuse_angle` statement.
     *
     * Ensures that `left() < right()`.
     */
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] bool numerical_only() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override;

    [[nodiscard]] const Angle &angle() const { return m_angle; }

    std::ostream &print(std::ostream &out) const override;

    auto operator<=>(const ObtuseAngle &other) const = default;
  private:
    Angle m_angle;
  };

}
