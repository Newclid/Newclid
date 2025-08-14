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
// -*- C++ -*-

#include "numbers/util.hpp"
#include "typedef.hpp"
#include <algorithm>
#include <bit>
#include <cmath>
#include <cstddef>
#include <optional>
#include <utility>

using namespace std;

namespace Yuclid {

  template<>
  bool approx_eq(const double& a, const double& b) {
    const double d = abs(a - b);
    return d < EPS || d < REL_TOL * max(abs(a), abs(b));
  }

  template<>
  bool approx_eq(const double& a, const Rat& b) {
    return approx_eq(a, rat2double(b));
  }

  template<>
  bool approx_eq(const double& a, const NNRat& b) {
    return approx_eq(a, nnrat2double(b));
  }

  optional<Nat> integer_sqrt(Nat n) {
    return integer_nth_root(n, 2);
  }

  optional<NNRat> rat_sqrt(NNRat r) {
    return rat_nth_root(r, Nat(2));
  }

  optional<Nat> integer_nth_root(Nat a, Nat n) {
    if (n == 0) {
      return 1;
    }

    if (n == 1 || a <= 1) {
      return a;
    }

    UnsafeNat const pow2 = (bit_width(UnsafeNat(a)) + n - 1) / UnsafeNat(n);
    Nat guess(UnsafeNat(1) << pow2);
    Nat next_guess = guess;

    do {
      guess = next_guess;
      next_guess = (a / upower(guess, n - 1) + (n - 1) * guess) / n;
    } while (next_guess < guess);
    if (upower(guess, n) == a) {
      return guess;
    }
    return nullopt;
  }

  optional<NNRat> rat_nth_root(NNRat r, Nat n) {
    optional<Int> num = integer_nth_root(r.numerator(), n);
    if (!num.has_value()) {
      return nullopt;
    }
    optional<Int> den = integer_nth_root(r.denominator(), n);
    if (!den.has_value()) {
      return nullopt;
    }
    return NNRat(num.value(), den.value());
  }

  std::pair<Nat, NNRat> get_rational_power(const NNRat& q, const Nat& max_k)
  {
    // Iterate through possible exponents 'k' from min(63, current_exp) down to 2.
    // The maximum k for which a long int can be a k-th power is around 63 (for 2^63).
    // Limiting by current_exp is an optimization for smaller exponents.
    for (Int k = std::min(Nat(63), max_k); k >= 2; --k) {
      std::optional<NNRat> root_found = rat_nth_root(q, k);
      if (root_found) {
        return {k, root_found.value()}; // Found the largest k and its root
      }
    }
    return {1, q};
  }

} // namespace Yuclid
