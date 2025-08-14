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
#include "equation_traits.hpp"
#include "numbers/posreal.hpp"
#include "equation.hpp"
#include "numbers/util.hpp"
#include "type/angle.hpp"
#include "type/dist.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"
#include <boost/preprocessor/seq/for_each.hpp>

namespace Yuclid {
  double EquationTraits<Dist>::eval_term(const Rat &c, const Dist &v) {
    return rat2double(c) * double(v);
  }

  double EquationTraits<SquaredDist>::eval_term(const Rat &c, const SquaredDist &v) {
    return rat2double(c) * double(v);
  }

  Posreal EquationTraits<SinOrDist>::eval_term(const Rat &c, const SinOrDist &v) {
    return c * Posreal(v);
  }

  AddCircle<double> EquationTraits<SlopeAngle>::eval_term(const Rat &c, const SlopeAngle &v) {
    return c * AddCircle<double>(v);
  }

  AddCircle<double> EquationTraits<Angle>::eval_term(const Rat &c, const Angle &v) {
    return c * AddCircle<double>(v);
  }

  template<typename VarT>
  Equation<VarT> EquationTraits<EqnIndex<VarT>>::eval_term(const Rat &c, const EqnIndex<VarT> &v) {
    return c * v.equation();
  }

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQUATION_TRAITS, /* empty */, YUCLID_EQN_INDEX_TYPES)
}
