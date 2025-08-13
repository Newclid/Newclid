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

namespace boost {
#ifdef WITH_SAFE_NUMERICS
  template <typename t>
  inline auto operator<=>(const boost::safe_numerics::safe<t> &lhs,
                          const boost::safe_numerics::safe<t> &rhs) {
    return static_cast<t>(lhs) <=> static_cast<t>(rhs);
  }
#endif

  /** Provide a missing `operator<=>` for `boost::rational`. */
  template <typename t>
  inline auto operator<=>(const rational<t> &lhs, const rational<t> &rhs) {
    return lhs.numerator() * rhs.denominator() <=> rhs.numerator() * lhs.denominator();
  }
}

#if 0
/** Provide a missing `operator<=>` for `mpq_class`. */
inline auto operator<=>(const mpq_class &lhs, const mpq_class &rhs) {
  return cmp(lhs, rhs) <=> 0;
}
#endif
