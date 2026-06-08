#pragma once

#include <cstddef>
#include <limits>

namespace Yuclid {

    using RuleVariableIndex = std::size_t;
    using ProblemPointIndex = std::size_t;

    /**
     * Sentinel value used in m_point_by_variable to mark that a rule variable
     * is currently not assigned to any problem point.
     */
    static constexpr ProblemPointIndex UNASSIGNED_POINT =
        std::numeric_limits<ProblemPointIndex>::max();

}
