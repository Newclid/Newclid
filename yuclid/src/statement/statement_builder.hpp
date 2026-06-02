/**
 * Note on Constant Parsing (JGEX Compatibility):
 * ----------------------------------------------
 * This statement builder intentionally mirrors the behavior of the legacy 
 * Problem parser when handling fractional constants (used in rconst, aconst, etc.).
 * * The underlying `boost::rational` stream extraction expects strict "a/b" formatting.
 * If a malformed constant is provided, the stream sets a failbit. 
 * Following the way the engine historically processed JGEX files, 
 * we DO NOT throw a `std::runtime_error` on failure. 
 * * Instead, failures are swallowed silently, and the constant defaults to 0/1.
 * * Cases that silently default to 0/1:
 * - Division by zero (e.g., "2/0")
 * - Whole integers (e.g., "3")
 * * Note: Severe malformations (like "/5", "5/", "5/abc") will bypass the stream failbit
 * and trigger a std::system_error (domain error) exactly as they did in the legacy parser.
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
