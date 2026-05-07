#pragma once

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/statement.hpp"

namespace Yuclid {
namespace {

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

    Point mapped_point(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t index
    ) {
        const std::string &variable = pattern.args.at(index);

        RuleMapping::const_iterator iterator = mapping.find(variable);
        if(iterator == mapping.end()) {
            throw std::runtime_error(
                std::format(
                    "Predicate {} uses variable {}, but it is missing from rule mapping.",
                    pattern.name,
                    variable
                )
            );
        }

        return iterator->second;
    }

}
    std::unique_ptr<Statement> build_statement_from_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping
    );

}
