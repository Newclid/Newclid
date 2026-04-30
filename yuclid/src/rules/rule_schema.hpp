#pragma once

#include <string>
#include <vector>

#include "statement_patterns.hpp"

namespace Yuclid {

    struct RuleSchema {
        std::string name;
        std::vector<PointVar> variables;
        std::vector<StatementPattern> hypotheses;
        std::vector<StatementPattern> conclusions;
    };
}
