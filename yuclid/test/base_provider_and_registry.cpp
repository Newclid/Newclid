#define BOOST_TEST_MODULE base_provider_and_registry_test

#include <boost/test/unit_test.hpp>

#include "matchers/predicate_provider.hpp"
#include "matchers/base_provider.hpp"
#include "problem.hpp"
#include "matchers/lazy_geometry_cache.hpp"
#include "matchers/mapping_state.hpp"
#include "matchers/rule_plan.hpp"
#include "rules/rule_schema.hpp"

using namespace Yuclid;

// Registry tests (Using a Dummy Provider)
// A dummy provider just so we can verify memory addresses and routing in the registry
class DummyProvider : public PredicateProvider {
public:
    std::size_t id;
    DummyProvider(std::size_t identifier) : id(identifier) {}

    std::size_t estimate_extensions(const PlannedPredicate&, const MappingState&, const LazyGeometryCache&) const override { return id; }
    std::generator<MappingExtension> generate_extensions(const PlannedPredicate&, const MappingState&, const LazyGeometryCache&) const override { co_return; }
    bool is_satisfied(const PlannedPredicate&, const MappingState&, const LazyGeometryCache&) const override { return true; }
};

BOOST_AUTO_TEST_SUITE(registry_suite)

BOOST_AUTO_TEST_CASE(registry_null_fallback_throws) {
    BOOST_CHECK_THROW(PredicateProviderRegistry(nullptr), std::runtime_error);
}

BOOST_AUTO_TEST_CASE(registry_routes_to_fallback) {
    auto fallback = std::make_unique<DummyProvider>(999);
    PredicateProviderRegistry registry(std::move(fallback));

    // Requesting a predicate that hasn't been registered should return the fallback
    const PredicateProvider* provider = registry.get_provider("unregistered_pred");
    BOOST_REQUIRE(provider != nullptr);
    
    // Cast to DummyProvider to verify it's our fallback
    const DummyProvider* dummy = dynamic_cast<const DummyProvider*>(provider);
    BOOST_REQUIRE(dummy != nullptr);
    BOOST_CHECK_EQUAL(dummy->id, 999);
}

BOOST_AUTO_TEST_SUITE_END()