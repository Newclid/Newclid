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
#include "ar/equation.hpp"
#include "typedef.hpp"

namespace Yuclid {
  class LineAngleEq;

  /**
   * @brief Predicate saying \f$\angle ABC=r\pi\f$.
   *
   * The notion is well-defined if \f$A \ne B\f$ and \f$B \ne C\f$.
   * The angle is understood as the oriented angle
   * between the lines \f$AB\f$ and \f$BC\f$,
   * defined modulo \f$\pi\f$.
   *
   * @todo Migrate to Mathlib-style oriented angles between vectors.
   */
  class AngleEq : public Statement {
  public:
    /**
     * @brief Construct `AngleEq` from an `Angle` and an `AddCircle` value.
     *
     * Constructs a statement saying that the value of `ang` is `val` times `π`.
     *
     * @param ang the angle;
     * @param val the value of the angle, as a fraction of `π`.
     */
    AngleEq(const Angle &ang, const AddCircle<Rat> &val);
    /**
     * @brief Construct `AngleEq` from an `Angle` and an `AddCircle` value.
     *
     * Constructs a statement saying that the value of `ang` is `val` times `π`.
     * This version takes `val` as a rational number
     * without an `AddCircle` wrapper.
     *
     * @param ang the angle;
     * @param val the value of the angle, as a fraction of `π`.
     */
    AngleEq(const Angle &ang, const Rat &val);

    /**
     * @brief Name of the predicate
     *
     * The name of the predicate is `aconst`.
     */
    [[nodiscard]] std::string name() const override;

    /**
     * @brief Points used in the predicate.
     *
     * @returns The vertices of the angle.
     */
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    [[nodiscard]] LineAngleEq to_line_angle_eq() const;

    // Public read-only access methods
    [[nodiscard]] const Angle &angle() const { return m_angle; }
    [[nodiscard]] const AddCircle<Rat> &rhs() const { return m_rhs; }
    auto operator<=>(const AngleEq &other) const = default;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<AngleEq>(*this);
    }

    [[nodiscard]] boost::json::object to_json() const override;
    std::ostream &print(std::ostream &out) const override;

    ~AngleEq() override = default;

  protected:
    [[nodiscard]] std::optional<Equation<SlopeAngle>>
    as_equation_slope_angle() const override;

  private:
    Angle m_angle;
    AddCircle<Rat> m_rhs;
  };

} // namespace Yuclid
