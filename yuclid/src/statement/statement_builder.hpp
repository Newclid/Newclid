#pragma once

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/statement.hpp"
#include <memory>

namespace Yuclid {
    [[nodiscard]] std::unique_ptr<Statement> build_statement_from_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping
    );
}
