#pragma once

#include <cstddef>
#include <functional>
#include <memory>
#include <string>
#include <unordered_map>
#include <generator>

#include "predicate_matching_metadata.hpp"
#include "mapping_state.hpp"

namespace Yuclid{

struct ProblemGeometryCache {};

class PredicateProvider {
public:
    virtual ~PredicateProvider() = default;

    [[nodiscard]] virtual std::size_t estimate_extensions(
        const RulePredicatePattern &pattern,
        const MappingState &mapping,
        const ProblemGeometryCache &index,
        PredicateMatchingMetadata predicate
    ) const = 0;

    virtual std::generator<MappingExtension> generate_extensions(
        const RulePredicatePattern &pattern,
        const MappingState &mapping,
        const ProblemGeometryCache &index
    ) const = 0;

    [[nodiscard]] virtual bool is_satisfied(
        const RulePredicatePattern &pattern,
        const MappingState &mapping,
        const ProblemGeometryCache &index
    ) const = 0;
};

}