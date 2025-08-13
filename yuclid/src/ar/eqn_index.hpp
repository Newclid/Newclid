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
#include <cstddef>   // For size_t
#include <ostream>   // For std::ostream
#include <boost/preprocessor.hpp>

#include "type/variable_types.hpp"

// Forward declaration of equation to avoid circular include for its full definition
namespace Yuclid {
  template <typename VarT> class Equation;
  template <typename VarT> class LinearSystem;
  class Dist;
  class SquaredDist;
  class SinOrDist;
  class SlopeAngle;

  /**
   * @brief Represents an index for an equation within a LinearSystem.
   *
   * This class wraps a `size_t` index, providing a type-safe way to refer
   * to specific equations in a `LinearSystem` for a given `VarT`.
   * It provides defaulted comparison operators and a simple getter for the
   * underlying index.
   *
   * @tparam VarT The type of the geometric variable associated with the equation.
   */
  template <typename VarT>
  class EqnIndex final {
  private:
    size_t m_data; /**< The underlying index of the equation. */
    /** The system where this equation is one of the "original" equations. */
    const LinearSystem<VarT> *m_system;

  public:
    /**
     * @brief Constructs an `EqnIndex` from a `size_t` value.
     * @param ind The index of the equation.
     */
    constexpr EqnIndex(size_t ind, const LinearSystem<VarT> *s) :
      m_data(ind), m_system(s) {};

    /**
     * @brief Gets the raw `size_t` index.
     * @return The underlying `size_t` index.
     */
    [[nodiscard]] constexpr size_t get() const { return m_data; };

    /**
     * @brief Get the linear system that contains this equation.
     */
    constexpr const LinearSystem<VarT> *get_system() { return m_system; }

    /**
     * @brief Gets the equation corresponding to this index from the global linear system.
     * This method requires `linear_system.hpp` to be included by any `.cpp` file
     * that instantiates or uses this method, as it depends on `LinearSystem`'s definition.
     * @return A const reference to the equation.
     * @throws std::out_of_range if the index is invalid in the linear system.
     */
    [[nodiscard]] const Equation<VarT>& equation() const;

    /**
     * @brief Compares two `EqnIndex` objects based on their underlying index.
     * Provides default three-way comparison.
     */
    auto operator<=>(const EqnIndex& other) const = default;
  };

  /**
   * @brief Overloads the output stream operator for `EqnIndex` objects.
   * Prints the index as "Eq[index]: [equation_content]".
   * @tparam VarT The variable type of the equation.
   * @param os The output stream.
   * @param idx The `EqnIndex` object to print.
   * @return The output stream.
   */
  template <typename VarT>
  std::ostream& operator<<(std::ostream& os, const EqnIndex<VarT>& idx);

} // namespace Yuclid

#define YUCLID_INSTANTIATE_EQN_INDEX(r, prefix, VarT)   \
  prefix template class Yuclid::EqnIndex<VarT>;         \
  prefix template std::ostream&                         \
  Yuclid::operator<<(std::ostream& os,                  \
                     const Yuclid::EqnIndex<VarT>&);

BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQN_INDEX, extern,    \
                      YUCLID_EQN_VARIABLE_TYPES)
