#pragma once

#include <cstddef>
#include <string>
#include <variant>

namespace Yuclid {

    struct PointVar {
        std::size_t id;
        std::string name;
    };

        using StatementPattern = std::variant<
        PointVar
    >;
}
