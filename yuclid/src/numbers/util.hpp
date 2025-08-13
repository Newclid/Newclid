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

#include "typedef.hpp"
#include <array>
#include <utility>
#include <boost/algorithm/algorithm.hpp>

namespace Yuclid {

  const double EPS = 1E-7;
  const double REL_TOL = 1E-3;

  template<typename lhs_t, typename rhs_t>
  bool approx_eq(const lhs_t& lhs, const rhs_t& rhs);

  template<>
  bool approx_eq(const double& lhs, const double& rhs);

  template<>
  bool approx_eq(const double& lhs, const Rat& rhs);

  template<>
  bool approx_eq(const double& lhs, const NNRat& rhs);

  /**
   * @brief Returns the list of well-known values of `\sin²(rπ)` for rational `r`.
   */
  constexpr std::array<std::pair<Rat, NNRat>, 4> known_sin_squares() {
    return {
      std::make_pair(Rat(1, 6), NNRat(1, 4)),   // \sin²(π / 6) = 1 / 4
      std::make_pair(Rat(1, 4), NNRat(1, 2)),   // \sin²(π / 4) = 1 / 2
      std::make_pair(Rat(1, 3), NNRat(3, 4)),   // \sin²(π / 3) = 3 / 4
      std::make_pair(Rat(1, 2), 1)             // \sin²(π / 2) = 1
    };
  }
  
#define BASE_FIELDS (Rat)(double)

  /**
   * @brief Calculates the integer square root of a integer.
   *
   * This function attempts to find the integer square root of a given non-negative
   * integer. It returns an `std::optional<integer>` which will contain:
   * - The integer square root if the input is a perfect square.
   * - An empty optional (std::nullopt) if the input is negative or not a perfect square.
   *
   * @param n The integer number for which to find the square root.
   * @return An std::optional<integer> containing the integer square root, or empty.
   */
  std::optional<Nat> integer_sqrt(Nat n);

  /**
   * @brief Calculates the rational square root of a nonnegative rational.
   *
   * This function attempts to find the rational square root of a given non-negative
   * rational number. It returns an `std::optional<NNRat>` which will contain:
   * - The rational square root if both its numerator and denominator are perfect squares.
   * - An empty optional (std::nullopt) if the numerator or the denominator is not a perfect square.
   *
   * @param r The rational number for which to find the square root.
   * @return An std::optional<rat> containing the rational square root, or empty.
   */
  std::optional<NNRat> rat_sqrt(NNRat r);

  /**
   * @brief Calculates `n`th root of an integer `a`.
   *
   * The current implementation uses Newton-Raphson iterations
   * with the initial guess made using  `std::bit_width`.
   */
  std::optional<Nat> integer_nth_root(Nat a, Nat n);

  /**
   * @brief Calculates `n`th root of a rational `r`.
   */
  std::optional<NNRat> rat_nth_root(NNRat r, Nat n);

  /**
   * @brief Finds a representation `q = r ^ k` with the largest integer `k <= max_k`.
   *
   * If `q` is not a power of another rational, then returns `k = 1`, `r = q`.
   *
   * @param q The rational number to check.
   * @param max_k An upper estimate on `k` we may be interested in.
   * @return A pair: first is the largest integer k, second is the rational root.
   */
  std::pair<Nat, NNRat> get_rational_power(const NNRat& q, const Nat& max_k);

  inline double rat2double(const Rat &q) {
    return static_cast<double>(static_cast<UnsafeInt>(q.numerator())) /
      static_cast<double>(static_cast<UnsafeInt>(q.denominator()));
  }

  inline double nnrat2double(const NNRat &q) {
    return static_cast<double>(static_cast<UnsafeNat>(q.numerator())) /
      static_cast<double>(static_cast<UnsafeNat>(q.denominator()));
  }

  inline std::string rat2string(const Rat &q) {
    return std::format("{}/{}",
                       static_cast<UnsafeInt>(q.numerator()),
                       static_cast<UnsafeInt>(q.denominator()));
  }

  inline std::string nnrat2string(const NNRat &q) {
    return std::format("{}/{}",
                       static_cast<UnsafeNat>(q.numerator()),
                       static_cast<UnsafeNat>(q.denominator()));
  }

  inline NNRat rat2nnrat(const Rat &q) {
    return {static_cast<Nat>(q.numerator()),
            static_cast<Nat>(q.denominator())};
  }

  inline Rat nnrat2rat(const NNRat &q) {
    return {static_cast<Int>(q.numerator()),
            static_cast<Int>(q.denominator())};
  }

  template <typename T>
  T upower(T base, Nat exp) {
    return boost::algorithm::power(base, static_cast<UnsafeNat>(exp));
  }

  template <typename T>
  T zpower(T base, Int exp) {
    if (exp >= 0) {
      return boost::algorithm::power(base, static_cast<UnsafeInt>(exp));
    }
    return T(1) / boost::algorithm::power(base, static_cast<UnsafeInt>(-exp));
  }

} // namespace Yuclid
