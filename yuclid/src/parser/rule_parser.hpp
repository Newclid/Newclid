#pragma once
#include "rules/rule_schema.hpp"
#include <optional>

namespace Yuclid {
    [[nodiscard]] RulePredicatePattern parse_rule_predicate(std::istream &stream);
     void add_current_rule(
        std::optional<RuleSchema> &currentRule,
        std::vector<RuleSchema> &rules
    );
    [[nodiscard]] std::vector<RuleSchema> parse_rule_schemas(std::istream& input);
};
