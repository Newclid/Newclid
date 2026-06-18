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

/**
 * @brief Marking a filter flips only that index to "used".
 */
BOOST_AUTO_TEST_CASE(mark_sets_only_target) {
    FilterState state(4);
    state.mark_used(2);

    BOOST_CHECK(state.is_used(2));
    BOOST_CHECK(!state.is_used(0));
    BOOST_CHECK(!state.is_used(1));
    BOOST_CHECK(!state.is_used(3));
}

/**
 * @brief Several independent filters can be marked.
 */
BOOST_AUTO_TEST_CASE(mark_multiple) {
    FilterState state(4);
    state.mark_used(0);
    state.mark_used(3);

    BOOST_CHECK(state.is_used(0));
    BOOST_CHECK(!state.is_used(1));
    BOOST_CHECK(!state.is_used(2));
    BOOST_CHECK(state.is_used(3));
}

/**
 * @brief Marking the same filter twice is idempotent.
 */
BOOST_AUTO_TEST_CASE(mark_is_idempotent) {
    FilterState state(2);
    state.mark_used(1);
    state.mark_used(1);
    BOOST_CHECK(state.is_used(1));
}

/**
 * @brief Rollback unmarks exactly the filters marked since the snapshot.
 *
 * Mirrors search(): a filter passed at a shallow level stays marked across the
 * child call, and marks made inside the child are undone on backtrack.
 */
BOOST_AUTO_TEST_CASE(rollback_unmarks_filters_since_snapshot) {
    FilterState state(3);
    state.mark_used(0);  // "parent" level

    const auto snapshot = state.snapshot();

    state.mark_used(1);  // "child" level
    BOOST_CHECK(state.is_used(1));

    state.rollback(snapshot);

    BOOST_CHECK(state.is_used(0));   // parent mark survives
    BOOST_CHECK(!state.is_used(1));  // child mark undone
    BOOST_CHECK(!state.is_used(2));
}

/**
 * @brief Rolling back to a pristine snapshot clears every mark.
 */
BOOST_AUTO_TEST_CASE(rollback_to_pristine) {
    FilterState state(3);
    const auto pristine = state.snapshot();

    state.mark_used(0);
    state.mark_used(2);
    state.rollback(pristine);

    for (size_t i = 0; i < 3; ++i) {
        BOOST_CHECK(!state.is_used(i));
    }
}

BOOST_AUTO_TEST_SUITE_END()
