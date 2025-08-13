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
#include <boost/container_hash/hash_fwd.hpp>
#ifdef WITH_SAFE_NUMERICS
#include <exception> //NOLINT
#include <boost/container_hash/hash.hpp>
#include <boost/safe_numerics/safe_integer.hpp>
#endif
#include "numbers/rational.hpp"
#include <variant>

/**
 * @file Common type synonyms.
 *
 * This file forward-declares some types and defines type synonyms about them.
 */

namespace Yuclid {
  class Angle;
  class Dist;
  class Point;
  class RootRat;
  class SinOrDist;
  class SlopeAngle;
  class SquaredDist;
  class StatementProof;
  class Triangle;
  struct StatementData;
  template<typename t> class AddCircle;

  using UnsafeInt = int64_t;
  using UnsafeNat = uint64_t;

  /** Signed integer numbers we use throughout the program. */
#ifdef WITH_SAFE_NUMERICS
  using Int = boost::safe_numerics::safe<UnsafeInt>;
#else
  using Int = UnsafeInt;
#endif

#ifdef WITH_SAFE_NUMERICS
  using Nat = boost::safe_numerics::safe<UnsafeNat>;
#else
  using Nat = UnsafeNat;
#endif

  /**
   * @brief Rational numbers type we use in most parts of the program.
   *
   * The RHS of `equation<SinOrDist>` uses `RootRat`
   * which uses `boost::rational<uinteger>`.
   */
  using Rat = boost::rational<Int>;

  using NNRat = boost::rational<Nat>;

  /**
   * @brief allowed arguments for statements.
   *
   * It is possible to encode the arguments of every statement
   * by a sequence of integers,
   * but we prefer to use meaningful type wrappers directly.
   */
  using statement_arg = std::variant<
    AddCircle<Rat>,
    Angle,
    Dist,
    NNRat,
    Point,
    Rat,
    RootRat,
    SinOrDist,
    SlopeAngle,
    SquaredDist,
    Triangle,
    bool>;
}

namespace boost {

  inline size_t hash_value(const Yuclid::Rat& val) {
    size_t seed = 0;
    hash_combine<Yuclid::UnsafeInt>(seed, static_cast<Yuclid::UnsafeInt>(val.numerator()));
    hash_combine<Yuclid::UnsafeInt>(seed, static_cast<Yuclid::UnsafeInt>(val.denominator()));
    return seed;
  }

  inline size_t hash_value(const Yuclid::NNRat& val) {
    size_t seed = 0;
    hash_combine<Yuclid::UnsafeNat>(seed, static_cast<Yuclid::UnsafeNat>(val.numerator()));
    hash_combine<Yuclid::UnsafeNat>(seed, static_cast<Yuclid::UnsafeNat>(val.denominator()));
    return seed;
  }

}
