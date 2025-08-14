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

  class NonCollinear : public Statement {
  public:
    NonCollinear(Point a, Point b, Point c);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const Point& a() const { return m_a; }
    [[nodiscard]] const Point& b() const { return m_b; }
    [[nodiscard]] const Point& c() const { return m_c; }
    auto operator<=>(const NonCollinear &other) const = default;

    [[nodiscard]] bool check_equations() const override { return true; }
    [[nodiscard]] bool numerical_only() const override { return true; }
    std::ostream &print(std::ostream &out) const override;
    std::ostream &print_newclid(std::ostream &out) const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<NonCollinear>(*this);
    }

    ~NonCollinear() override = default;

  protected:
    Point m_a;
    Point m_b;
    Point m_c;
  };

} // namespace Yuclid
