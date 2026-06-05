#pragma once

#include "predicate_provider.hpp"
#include "predicate_matching_metadata.hpp"
#include "mapping_state.hpp"

namespace Yuclid {

    class BaseProvider : public PredicateProvider {
    public:
        [[nodiscard]] std::size_t estimate_extensions(
            const RulePredicatePattern &pattern,
            const MappingState &mapping,
            const ProblemGeometryCache &cache,
            const PredicateMatchingMetadata &predicate_metadata
        ) const override;

        [[nodiscard]] std::generator<MappingExtension> generate_extensions(
            const RulePredicatePattern &pattern,
            const MappingState &mapping,
            const ProblemGeometryCache &cache
        ) const override;

        [[nodiscard]] bool is_satisfied(
            const RulePredicatePattern &pattern,
            const MappingState &mapping,
            const ProblemGeometryCache &cache
        ) const override;
    };

}
