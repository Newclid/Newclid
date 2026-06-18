#define BOOST_TEST_MODULE filter_state_test
#include <boost/test/unit_test.hpp>

#include <stdexcept>

#include "matchers/filter_state.hpp"

using namespace std;
using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(filter_state_suite)

/**
 * @brief A freshly constructed FilterState has no filter marked as passed.
 */
BOOST_AUTO_TEST_CASE(fresh_state_all_unused) {
  FilterState state(3);
  for (size_t i = 0; i < 3; ++i) {
    BOOST_CHECK(!state.is_used(i));
  }
}

/**
 * @brief A plan with zero validators yields a valid, empty FilterState.
 */
BOOST_AUTO_TEST_CASE(zero_validators_ok) {
  BOOST_CHECK_NO_THROW(FilterState(0));
}

/**
 * @brief The bitset-backed state rejects more than 64 validators.
 */
BOOST_AUTO_TEST_CASE(validator_count_ceiling_throws) {
  BOOST_CHECK_NO_THROW(FilterState(64));               // at the limit
  BOOST_CHECK_THROW(FilterState(65), std::invalid_argument);  // one over
}

BOOST_AUTO_TEST_SUITE_END()
