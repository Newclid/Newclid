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


class PredicateProviderRegistry {
    public:
        PredicateProviderRegistry(std::unique_ptr<PredicateProvider> fallback_provider);
        void register_provider(const std::string& predicate_name, std::unique_ptr<PredicateProvider> provider);
        [[nodiscard]] PredicateProvider* get_provider(const std::string& predicate_name) const;

    private:
        std::unordered_map<std::string, std::unique_ptr<PredicateProvider>> m_providers;
        std::unique_ptr<PredicateProvider> m_fallback_provider;
};

}