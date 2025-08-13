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
#include <map>
#include <compare> // For operator<=>
#include "statement.hpp"
#include "ar/equation.hpp"
#include "typedef.hpp"
#include <stdexcept> // For std::invalid_argument

namespace Yuclid {

  template<typename VarT>
  class EqnStatement : public Statement {
  public:
    explicit EqnStatement(const std::vector<statement_arg>& args); // Modified explicit constructor
    explicit EqnStatement(const Equation<VarT> &data);
    explicit EqnStatement(Equation<VarT> &&data);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;

    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override; // Added clone() declaration

    // Public read-only access method
    [[nodiscard]] const Equation<VarT>& equation() const { return m_eqn; }

    std::ostream &print(std::ostream &out) const override;

    // Defaulted three-way comparison operator (requires equation<VarT> to also have it)
    auto operator<=>(const EqnStatement &other) const = default;

  protected:
    // Specific as_equation methods for different VarT types
    [[nodiscard]] std::optional<Equation<Dist>> as_equation_dist() const override;
    [[nodiscard]] std::optional<Equation<SquaredDist>> as_equation_squared_dist() const override;
    [[nodiscard]] std::optional<Equation<SlopeAngle>> as_equation_slope_angle() const override;
    [[nodiscard]] std::optional<Equation<SinOrDist>> as_equation_sin_or_dist() const override;

  private:
    Equation<VarT> m_eqn;
  };

#define YUCLID_INSTANTIATE_EQN_STATEMENT(r, prefix, VarT)       \
  prefix template class EqnStatement<VarT>;                     \

#define YUCLID_STATEMENT_VARIABLE_TYPES         \
  (Dist)(SquaredDist)(SinOrDist)(Angle)

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQN_STATEMENT, extern, \
                        YUCLID_STATEMENT_VARIABLE_TYPES)

} // namespace Yuclid
