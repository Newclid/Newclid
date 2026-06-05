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

    /**
    * @brief Abstract interface for predicate-specific optimized matching.
    * 
    * The generic matcher asks a PredicateProvider to generate or verify mappings using 
    * the ProblemGeometryCache. Most custom geometric predicates (e.g. coll, cong) 
    * should (eventually) have their own provider implementations.
    */
    class PredicateProvider {
    public:
        virtual ~PredicateProvider() = default;

        /**
        * @brief Estimates the number of candidate extensions this predicate can generate.
        * 
        * The matcher uses this to dynamically choose the cheapest predicate
        * to expand next.
        *  
        * @param pattern The specific rule predicate being evaluated (e.g., "coll A B C").
        * @param mapping The current state of assigned points to variables.
        * @param cache The geometry cache.
        * @param predicate_metadata Metadata containing base costs and roles.
        * @return std::size_t The estimated number of branches (mapping extensions) this predicate will create.
        */
        [[nodiscard]] virtual std::size_t estimate_extensions(
            const RulePredicatePattern &pattern,
            const MappingState &mapping,
            const ProblemGeometryCache &cache,
            const PredicateMatchingMetadata predicate_metadata
        ) const = 0;

        /**
        * @brief Generates new partial mappings by binding unassigned variables in the pattern.
        * 
        * Uses a generator pattern.
        * 
        * @param pattern The specific rule predicate being evaluated.
        * @param mapping The current state of assigned points to variables.
        * @param cache The geometry cache used to find valid points.
        * @return a generator that produces mapping extensions
        */
        virtual std::generator<MappingExtension> generate_extensions(
            const RulePredicatePattern &pattern,
            const MappingState &mapping,
            const ProblemGeometryCache &cache
        ) const = 0;

        /**
        * @brief Verifies if the geometric constraint holds true for fully assigned variables.
        * 
        * Used primarily for filters or validator predicates. 
        * It allows the matcher to prune invalid branches as early as possible 
        * before generating the rest of the rule variables.
        * 
        * @param pattern The specific rule predicate to check.
        * @param mapping The mapping state containing the fully bound variables for this pattern.
        * @param cache The geometry cache to verify the geometry.
        * @return true If the geometric constraint is valid.
        * @return false If the constraint fails.
        */
        [[nodiscard]] virtual bool is_satisfied(
            const RulePredicatePattern &pattern,
            const MappingState &mapping,
            const ProblemGeometryCache &cache
        ) const = 0;
    };


    /**
    * @brief Factory and registry for looking up PredicateProviders at runtime.
    * 
    * Maps string-based predicate names (e.g., "coll", "cong") to their specific 
    * provider implementations.
    */
    class PredicateProviderRegistry {
        public:
            /**
             * @brief Constructs the registry with a mandatory fallback provider.
             * 
             * @param fallback_provider The provider to return if a requested predicate does not have an associated provider. 
             */
            PredicateProviderRegistry(std::unique_ptr<PredicateProvider> fallback_provider);

            /**
            * @brief Registers a new provider for a specific predicate.
            * 
            * Overwrites any existing provider assigned to the given predicate name.
            * 
            * @param predicate_name The string identifier (e.g., "coll").
            * @param provider Unique pointer to the provider implementation.
            */
            void register_provider(const std::string& predicate_name, std::unique_ptr<PredicateProvider> provider);

            /**
            * @brief Retrieves a raw pointer to the requested provider.
            * 
            * @param predicate_name The string identifier of the predicate to look up.
            * @return PredicateProvider* Pointer to the requested provider, or the fallback provider 
            * if the name is not registered.
            */
            [[nodiscard]] PredicateProvider* get_provider(const std::string& predicate_name) const;

        private:
            std::unordered_map<std::string, std::unique_ptr<PredicateProvider>> m_providers;
            std::unique_ptr<PredicateProvider> m_fallback_provider;
    };

}