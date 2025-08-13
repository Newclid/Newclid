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
#include <compare> // For operator<=>
#include "statement.hpp"
#include "typedef.hpp" // Assuming point is defined here
#include "equal_angles.hpp"        // Required for returning equal_angles objects
#include <stdexcept>          // For std::invalid_argument

namespace Yuclid {

  class CyclicQuadrangle : public Statement {
  public:
    CyclicQuadrangle(Point a, Point b, Point c, Point d); // Renamed parameters
    explicit CyclicQuadrangle(const std::vector<statement_arg>& args); // Added explicit constructor

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override;

    // Public read-only access methods for points
    [[nodiscard]] const Point& a() const { return m_a; }
    [[nodiscard]] const Point& b() const { return m_b; }
    [[nodiscard]] const Point& c() const { return m_c; }
    [[nodiscard]] const Point& d() const { return m_d; }

    // Statement-specific methods for cyclic quadrilateral angle equalities
    [[nodiscard]] EqualAngles equal_angles_cad_cbd() const;
    [[nodiscard]] EqualAngles equal_angles_bad_bcd() const;
    [[nodiscard]] EqualAngles equal_angles_abd_acd() const;

    std::ostream &print(std::ostream &out) const override;

  private:
    Point m_a; // Renamed private member
    Point m_b; // Renamed private member
    Point m_c; // Renamed private member
    Point m_d; // Renamed private member

    // Defaulted three-way comparison operator
    auto operator<=>(const CyclicQuadrangle &other) const = default;
  };

} // namespace Yuclid
