#include "base_provider.hpp"
#include "statement/statement_builder.hpp"
#include "predicate_matching_metadata.hpp"

namespace Yuclid {
    std::size_t BaseProvider::estimate_extensions(
        [[maybe_unused]] const RulePredicatePattern &pattern,
        [[maybe_unused]] const MappingState &mapping,
        [[maybe_unused]] const ProblemGeometryCache &cache,
        [[maybe_unused]] PredicateMatchingMetadata predicate_metadata
    ) const {
        return std::numeric_limits<std::size_t>::max();
    }
}