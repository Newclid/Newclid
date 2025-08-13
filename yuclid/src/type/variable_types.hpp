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

#define YUCLID_EQN_VARIABLE_TYPES               \
  (Yuclid::Dist)                                \
  (Yuclid::SquaredDist)                         \
  (Yuclid::SinOrDist)                           \
  (Yuclid::SlopeAngle)

#define YUCLID_VARIABLE_TYPES                   \
  YUCLID_EQN_VARIABLE_TYPES                     \
  (Yuclid::Angle)

#define YUCLID_EQN_INDEX(r, unused, VarT)       \
  (Yuclid::EqnIndex<VarT>)

#define YUCLID_EQUATION_TYPES                           \
  YUCLID_VARIABLE_TYPES                                 \
  BOOST_PP_SEQ_FOR_EACH(YUCLID_EQN_INDEX, /* */,        \
                        YUCLID_EQN_VARIABLE_TYPES)

#define YUCLID_LINEAR_COMBINATION_TYPES YUCLID_EQUATION_TYPES (size_t)
