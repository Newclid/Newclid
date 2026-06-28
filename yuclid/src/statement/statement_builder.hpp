/**
 * Note on Constant Parsing (JGEX Compatibility):
 * ----------------------------------------------
 * StatementBuilder intentionally mirrors ProblemParser when handling
 * fractional constants used in predicates such as rconst, r2const, lconst,
 * l2const, and aconst.
 *
 * Historically, Yuclid relied directly on boost::rational stream extraction.
 * Some inputs such as whole integers ("3") or division by zero ("2/0") are
 * kept as legacy behaviour and may default to 0/1 through the rational
 * extraction path.
 *
 * Clearly malformed fraction syntax such as "/5", "5/", "5/abc", or "a/5"
 * is rejected before stream extraction. This keeps ProblemParser and
 * StatementBuilder consistent across GCC/libstdc++, macOS GCC, and MSVC.
 */

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
