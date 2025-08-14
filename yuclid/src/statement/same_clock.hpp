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
#include "typedef.hpp" // Assuming point is defined here

namespace Yuclid {

  /**
   * @brief A statement saying that 2 triangles have the same orientation.
   */
  class SameClock : public Statement {
  public:
    SameClock(const Triangle &l, const Triangle &r);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    /**
     * @todo actually normalize
     */
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] bool check_equations() const override { return true; }
    [[nodiscard]] bool numerical_only() const override { return true; }

    // Public read-only access methods
    [[nodiscard]] const Triangle &left() const { return m_left; }
    [[nodiscard]] const Triangle &right() const { return m_right; }
    auto operator<=>(const SameClock &other) const = default;

    std::ostream &print(std::ostream &out) const override;
    std::ostream &print_newclid(std::ostream &out) const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<SameClock>(*this);
    }

    ~SameClock() override = default;

  protected:
    Triangle m_left, m_right;
  };

} // namespace Yuclid
