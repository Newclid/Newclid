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
#include "typedef.hpp"

namespace Yuclid {

  /**
   * @brief `num_left() : den_left() = num_right() : den_right()`
   *
   * Formally, this statement is interpreted
   * as `num_left() * den_right() = den_left() * num_right()` in theorems.
   * If all the involved `Dist` instances are nonzero,
   * then the two statements are equivalent.
   */
  class EqualRatios : public Statement {
  public:
    /**
     * @brief Construct an `EqualRatios` statement from `Dist` components.
     */
    EqualRatios(Dist num_left, Dist den_left, Dist num_right, Dist den_right);

    /**
     * @brief Predicate name is `eqratio`.
     */
    [[nodiscard]] std::string name() const override;
    /**
     * @brief Points involved in the statement.
     *
     * @return an `std::vector` with 8 points
     * used in the numerators and denominators.
     */
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<EqualRatios>(*this);
    }

    /**
     * @brief Numerator of the left fraction.
     */
    [[nodiscard]] const Dist& num_left() const { return m_num_left; }
    /**
     * @brief Denominator of the left fraction.
     */
    [[nodiscard]] const Dist& den_left() const { return m_den_left; }
    /**
     * @brief Numerator of the right fraction.
     */
    [[nodiscard]] const Dist& num_right() const { return m_num_right; }
    /**
     * @brief Denominator of the right fraction.
     */
    [[nodiscard]] const Dist& den_right() const { return m_den_right; }

    /**
     * @brief Print the object to `out`.
     *
     * @param out the output stream.
     */
    std::ostream &print(std::ostream &out) const override;

  protected:
    /**
     * @brief Interpret as an AR equation in the "ratios" table.
     */
    [[nodiscard]]
    std::optional<Equation<SinOrDist>>
    as_equation_sin_or_dist() const override;

  private:
    /**
     * @brief Numerator of the left fraction.
     */
    Dist m_num_left;
    /**
     * @brief Denominator of the left fraction.
     */
    Dist m_den_left;
    /**
     * @brief Numerator of the right fraction.
     */
    Dist m_num_right;
    /**
     * @brief Denominator of the right fraction.
     */
    Dist m_den_right;
  };

} // namespace Yuclid
