#define BOOST_TEST_MODULE provider_registry_test

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

BOOST_AUTO_TEST_CASE(registry_routes_to_specific_provider) {
    PredicateProviderRegistry registry(std::make_unique<DummyProvider>(999)); // Fallback
    
    registry.register_provider("cong", std::make_unique<DummyProvider>(1));
    registry.register_provider("para", std::make_unique<DummyProvider>(2));

    const DummyProvider* cong_prov = dynamic_cast<const DummyProvider*>(registry.get_provider("cong"));
    const DummyProvider* para_prov = dynamic_cast<const DummyProvider*>(registry.get_provider("para"));

    BOOST_REQUIRE(cong_prov != nullptr);
    BOOST_REQUIRE(para_prov != nullptr);
    BOOST_CHECK_EQUAL(cong_prov->id, 1);
    BOOST_CHECK_EQUAL(para_prov->id, 2);
}

BOOST_AUTO_TEST_CASE(registry_overwrites_existing_provider) {
    PredicateProviderRegistry registry(std::make_unique<DummyProvider>(999));
    
    registry.register_provider("coll", std::make_unique<DummyProvider>(10));
    registry.register_provider("coll", std::make_unique<DummyProvider>(20)); // Overwrite

    const DummyProvider* coll_prov = dynamic_cast<const DummyProvider*>(registry.get_provider("coll"));
    BOOST_REQUIRE(coll_prov != nullptr);
    BOOST_CHECK_EQUAL(coll_prov->id, 20);
}

BOOST_AUTO_TEST_SUITE_END()