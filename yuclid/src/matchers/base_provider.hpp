#pragma once

#include "predicate_provider.hpp"
#include "mapping_state.hpp"
#include "lazy_geometry_cache.hpp"

namespace Yuclid {

    /** @brief This class represents the default Provider.
     * It will be used for predicates that dont have a specific one implemented.
    */
    class BaseProvider : public PredicateProvider {
    public:
        [[nodiscard]] std::size_t estimate_extensions(
            const PlannedPredicate &predicate,
            const MappingState &mapping,
            const LazyGeometryCache &cache
        ) const override;

        [[nodiscard]] std::generator<MappingExtension> generate_extensions(
            const PlannedPredicate &predicate,
            const MappingState &mapping,
            const LazyGeometryCache &cache
        ) const override;

        [[nodiscard]] bool is_satisfied(
            const PlannedPredicate &predicate,
            const MappingState &mapping,
            const LazyGeometryCache &cache
        ) const override;
    };

}
