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
#include "similar_triangles.hpp"

namespace Yuclid {
  class DistEqDist;

  class CongruentTriangles : public SimilarTriangles {
  public:
    CongruentTriangles(const Triangle &t1, const Triangle &t2, bool same_clockwise);
    explicit CongruentTriangles(const std::vector<statement_arg>& args); // Added explicit constructor

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override; // Added clone() declaration

    [[nodiscard]] DistEqDist cong_ab() const;
    [[nodiscard]] DistEqDist cong_bc() const;
    [[nodiscard]] DistEqDist cong_ac() const;
    
    [[nodiscard]] EqualAngles equal_angles_abc() const;
    [[nodiscard]] EqualAngles equal_angles_bca() const;
    [[nodiscard]] EqualAngles equal_angles_cab() const;

    std::ostream &print(std::ostream &out) const override;

    // Defaulted three-way comparison operator
    auto operator<=>(const CongruentTriangles &other) const = default;
  };

} // namespace Yuclid
