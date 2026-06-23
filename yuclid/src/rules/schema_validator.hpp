#pragma once

#include <string>
#include <optional>

#include "rule_schema.hpp" 

namespace Yuclid {   
    // Returns std::nullopt if valid, or an error string if invalid.
    std::optional<std::string> validate_schema(const RuleSchema& schema);
}