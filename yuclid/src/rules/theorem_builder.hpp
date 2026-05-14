#pragma once

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "theorem.hpp"

namespace Yuclid {
    
    /**
     * @brief Create a theorem from rule schema and specific mapping of points
     */
    [[nodiscard]] Theorem build_theorem_from_rule_schema(
        const RuleSchema &schema,
        const RuleMapping &mapping
    );

}
