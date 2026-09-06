#pragma once
#include "rules/rule_schema.hpp"

namespace Yuclid {
    [[nodiscard]] std::vector<RuleSchema> parse_rule_schemas(std::istream& input);
};
