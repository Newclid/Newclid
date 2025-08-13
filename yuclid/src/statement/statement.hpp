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
#include "ar/equation.hpp"
#include "typedef.hpp"
#include "type/triangle.hpp"

namespace Yuclid {
  class Statement;
  class RatioSquaredDist;

  /** Data that uniquely determines a statement.

      This is useful to, e.g., read&write to/from JSON,
      or to generate `std::map` keys from a heterogeneous collection of statements.
   */
  struct StatementData {
    std::string name;
    std::vector<statement_arg> args;

    auto operator<=>(const StatementData &other) const = default;
  };

  /** A single statement.

      We use the same type for basic statements (e.g., `AB=CD`)
      as well for configurations from theorems.
   */
  class Statement {
  public:
    /** The name of the statement. */
    [[nodiscard]] virtual std::string name() const = 0;

    /** All points used in the statement. */
    [[nodiscard]] virtual std::vector<Point> points() const = 0;

    /** Return the normalized version of a statement.

        In most cases, it just reorders the arguments.
        In some cases, it simplifies, e.g., `AB:CD=AB:EF` to `CD=EF`.
    */
    [[nodiscard]] virtual std::unique_ptr<Statement> normalize() const = 0;

    /** Verify numerically the non-degenericity assumptions of the statement.

        E.g., for `|AB|=|CD|` it verifies `A \ne B` and `C \ne D`.
        For similar triangles, it verifies that they have the orientation stored in the statement, etc.
    */
    [[nodiscard]] virtual bool check_nondegen() const = 0;

    /** Verify numerically the equations involved in the statement.
     */
    [[nodiscard]] virtual bool check_equations() const = 0;

    /** Verify the statement numerically.

        This function calls both `check_nondegen` and `check_equations`.
     */
    [[nodiscard]] virtual bool check_numerically() const final {
      return this->check_nondegen() && this->check_equations();
    }

    /** @brief Creates a deep copy of the statement object.
     *
     * This is crucial for managing unique_ptr<Statement> in containers.
     */
    [[nodiscard]] virtual std::unique_ptr<Statement> clone() const = 0;

    virtual ~Statement() = default;

    /** Returns the arguments that uniquely identify this statement.
     */
    [[nodiscard]] virtual std::vector<statement_arg> args() const = 0;

    [[nodiscard]] virtual StatementData data() const final {
      return {.name=this->name(), .args=this->args()};
    }

    /** Returns true if this statement must not be used in theorems.
     *
     * Used for compound statements like `thales`.
     */
    [[nodiscard]] virtual bool banned_from_theorems() const {
      return false;
    }

    [[nodiscard]] virtual std::optional<RatioSquaredDist> as_ratio_squared_dist() const;

    /**
     * @brief Test if the statement is `a = a`.
     *
     * Default implementation returns `false`.
     */
    [[nodiscard]] virtual bool is_refl() const;

    /**
     * @brief Test if the statement is only verified numerically.
     *
     * The default implementation returns `false`.
     */
    [[nodiscard]] virtual bool numerical_only() const;

    auto operator<=>(const Statement &) const = default;

    virtual std::ostream &print(std::ostream &out) const = 0;

    /**
     * Export a statement to JSON.
     *
     * The default implementation yields `{"name" : name(), "points": points() }`.
     * Subclasses can override this method to improve compatibility with Newclid.
     */
    [[nodiscard]] virtual boost::json::object to_json() const;

    /**
     * @brief Print the statement in a format understood by Newclid.
     *
     * @todo Use `std::format` with modifiers for different formats instead of different functions.
     */
    virtual std::ostream &print_newclid(std::ostream &out) const;

    template <typename VarT> std::optional<Equation<VarT>> as_equation() const;

  protected:
    [[nodiscard]]
    virtual std::optional<Equation<Dist>> as_equation_dist() const {
      return std::nullopt;
    }

    [[nodiscard]]
    virtual std::optional<Equation<SquaredDist>> as_equation_squared_dist() const {
      return std::nullopt;
    }

    [[nodiscard]]
    virtual std::optional<Equation<SlopeAngle>> as_equation_slope_angle() const {
      return std::nullopt;
    }

    [[nodiscard]]
    virtual std::optional<Equation<SinOrDist>> as_equation_sin_or_dist() const {
      return std::nullopt;
    }
  };

  template<>
  inline std::optional<Equation<Dist>> Statement::as_equation<Dist>() const {
    return as_equation_dist();
  }

  template<>
  inline std::optional<Equation<SquaredDist>> Statement::as_equation<SquaredDist>() const {
    return as_equation_squared_dist();
  }

  template<>
  inline std::optional<Equation<SlopeAngle>> Statement::as_equation<SlopeAngle>() const {
    return as_equation_slope_angle();
  }

  template<>
  inline std::optional<Equation<SinOrDist>> Statement::as_equation<SinOrDist>() const {
    return as_equation_sin_or_dist();
  }

  std::ostream &operator<<(std::ostream &out, const Statement &p);
}

namespace std {

  /** `tag_invoke` for `std::unique_ptr<Statement>`.
   *
   * It must live in `std::` namespace
   */
  void tag_invoke(boost::json::value_from_tag /*unused*/, boost::json::value& jv,
                  const unique_ptr<Yuclid::Statement>& p);

}
