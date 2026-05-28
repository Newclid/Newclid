#pragma once

#include <memory>

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/statement.hpp"

namespace Yuclid {
    [[nodiscard]] std::vector<std::unique_ptr<Statement>> build_statements_from_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping
    );
}
