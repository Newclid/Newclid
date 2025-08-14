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
#include "statement.hpp"
#include "typedef.hpp"
#include "equal_angles.hpp"
#include "eqratio.hpp"

namespace Yuclid {
  class SameClock;

  class SimilarTriangles : public Statement {
  public:
    SimilarTriangles(const Triangle &t1, const Triangle &t2, bool same_clockwise);
    explicit SimilarTriangles(const std::vector<statement_arg>& args); // Added explicit constructor

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override; // Added clone() declaration

    // Public read-only access methods
    [[nodiscard]] const Triangle& left() const { return m_left; }
    [[nodiscard]] const Triangle& right() const { return m_right; }
    [[nodiscard]] bool same_clockwise() const { return m_same_clockwise; }
    [[nodiscard]] SameClock to_same_clock() const;

    [[nodiscard]] EqualRatios eqratio_abbc() const;
    [[nodiscard]] EqualRatios eqratio_abac() const;
    [[nodiscard]] EqualRatios eqratio_bcac() const;
    [[nodiscard]] EqualAngles equal_angles_abc() const;
    [[nodiscard]] EqualAngles equal_angles_bca() const;
    [[nodiscard]] EqualAngles equal_angles_acb() const;
    [[nodiscard]] EqualAngles equal_angles_cab() const;

    [[nodiscard]] std::array<SimilarTriangles, 12> permutations() const;
    [[nodiscard]] std::array<SimilarTriangles, 3> cyclic_rotations() const;
    std::ostream &print(std::ostream &out) const override;

    // Defaulted three-way comparison operator
    auto operator<=>(const SimilarTriangles &other) const = default;

  private:
    Triangle m_left;
    Triangle m_right;
    bool m_same_clockwise;
  };

} // namespace Yuclid
