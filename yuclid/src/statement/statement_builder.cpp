#pragma once

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/statement.hpp"
#include <format>

namespace Yuclid {

    void check_arity(const RulePredicatePattern &pattern, std::size_t expected) {
        if(pattern.args.size() != expected) {
            throw std::runtime_error(
                std::format("Predicate '{}' expects {} arguments, but got {}",
                    pattern.name,
                    expected,
                    pattern.args.size()
                )
            );
        }
    }

    std::unique_ptr<Statement> build_statement_from_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping
    );

}
