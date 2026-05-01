#pragma once

#include <string>
#include <vector>

namespace Yuclid {

    struct RulePredicatePattern {
        std::string name;
        std::vector<std::string> args;
    };

    struct RuleSchema {
        std::string id;
        std::vector<std::string> variables;
        std::vector<RulePredicatePattern> hypotheses;
        std::vector<RulePredicatePattern> conclusions;
    };
}
