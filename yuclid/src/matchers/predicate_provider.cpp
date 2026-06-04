#include "predicate_provider.hpp"


namespace Yuclid {
    PredicateProviderRegistry::PredicateProviderRegistry(std::unique_ptr<PredicateProvider> fallback_provider) 
        : m_fallback_provider(std::move(fallback_provider)) {}

    // Newly registered providers for the same predicate will overwrite the old ones
    void PredicateProviderRegistry::register_provider(const std::string& predicate_name, std::unique_ptr<PredicateProvider> provider) {
        m_providers.insert_or_assign(predicate_name, std::move(provider));
    }

    PredicateProvider* PredicateProviderRegistry::get_provider(const std::string& predicate_name) const {
        auto provider_iterator = m_providers.find(predicate_name);
        if(provider_iterator != m_providers.end()){
            return provider_iterator->second.get();
        }
        // If no provider has been found, return the fallback provider
        return m_fallback_provider.get();
    }
}