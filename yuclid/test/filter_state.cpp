#define BOOST_TEST_MODULE filter_state_test

#include <boost/test/unit_test.hpp>

#include <cstddef>
#include <stdexcept>

#include "matchers/filter_state.hpp"

using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(filter_state_suite)

/**
 * A freshly constructed FilterState has no filter marked as used.
 */
BOOST_AUTO_TEST_CASE(fresh_state_has_no_used_filters) {
    FilterState state(3);

    for (
        std::size_t filter_index = 0;
        filter_index < 3;
        ++filter_index
    ) {
        BOOST_CHECK(
            !state.is_used(filter_index)
        );
    }
}

/**
 * A state with no filters is valid, and every index remains unused.
 */
BOOST_AUTO_TEST_CASE(zero_filter_state_is_valid) {
    FilterState state(0);

    BOOST_CHECK(!state.is_used(0));

    state.mark_used(0);

    BOOST_CHECK(!state.is_used(0));
}

/**
 * Exactly 64 filters are supported.
 */
BOOST_AUTO_TEST_CASE(filter_count_at_limit_is_accepted) {
    BOOST_CHECK_NO_THROW(
        (void)FilterState(64)
    );
}

/**
 * More than 64 filters are rejected because the state uses a 64-bit mask.
 */
BOOST_AUTO_TEST_CASE(filter_count_above_limit_throws) {
    BOOST_CHECK_THROW(
        (void)FilterState(65),
        std::invalid_argument
    );
}

/**
 * The final valid filter index can be marked safely.
 */
BOOST_AUTO_TEST_CASE(highest_valid_filter_index_can_be_marked) {
    FilterState state(64);

    state.mark_used(63);

    BOOST_CHECK(state.is_used(63));
    BOOST_CHECK(!state.is_used(62));
}

/**
 * Marking one filter changes only that filter.
 */
BOOST_AUTO_TEST_CASE(mark_used_changes_only_target_filter) {
    FilterState state(4);

    state.mark_used(2);

    BOOST_CHECK(!state.is_used(0));
    BOOST_CHECK(!state.is_used(1));
    BOOST_CHECK(state.is_used(2));
    BOOST_CHECK(!state.is_used(3));
}

/**
 * Several independent filters can be marked as used.
 */
BOOST_AUTO_TEST_CASE(multiple_filters_can_be_marked) {
    FilterState state(4);

    state.mark_used(0);
    state.mark_used(3);

    BOOST_CHECK(state.is_used(0));
    BOOST_CHECK(!state.is_used(1));
    BOOST_CHECK(!state.is_used(2));
    BOOST_CHECK(state.is_used(3));
}

/**
 * Marking the same filter repeatedly is idempotent.
 */
BOOST_AUTO_TEST_CASE(mark_used_is_idempotent) {
    FilterState state(2);

    state.mark_used(1);
    state.mark_used(1);

    BOOST_CHECK(!state.is_used(0));
    BOOST_CHECK(state.is_used(1));
}

/**
 * Reading an out-of-range filter index returns false.
 */
BOOST_AUTO_TEST_CASE(out_of_range_filter_is_not_used) {
    FilterState state(3);

    BOOST_CHECK(!state.is_used(3));
    BOOST_CHECK(!state.is_used(100));
}

/**
 * Marking an out-of-range filter index has no effect.
 */
BOOST_AUTO_TEST_CASE(marking_out_of_range_filter_has_no_effect) {
    FilterState state(3);

    state.mark_used(3);
    state.mark_used(100);

    for (
        std::size_t filter_index = 0;
        filter_index < 3;
        ++filter_index
    ) {
        BOOST_CHECK(
            !state.is_used(filter_index)
        );
    }
}

/**
 * An invalid mark does not disturb existing valid marks.
 */
BOOST_AUTO_TEST_CASE(
    marking_out_of_range_filter_preserves_existing_state
) {
    FilterState state(3);

    state.mark_used(1);
    state.mark_used(3);

    BOOST_CHECK(!state.is_used(0));
    BOOST_CHECK(state.is_used(1));
    BOOST_CHECK(!state.is_used(2));
}

/**
 * Rollback restores the filter marks stored in the snapshot.
 *
 * Marks made before the snapshot remain, while marks made afterwards are
 * removed.
 */
BOOST_AUTO_TEST_CASE(
    rollback_restores_filters_from_snapshot
) {
    FilterState state(3);

    state.mark_used(0);

    const FilterStateSnapshot snapshot =
        state.snapshot();

    state.mark_used(1);

    BOOST_CHECK(state.is_used(0));
    BOOST_CHECK(state.is_used(1));

    state.rollback(snapshot);

    BOOST_CHECK(state.is_used(0));
    BOOST_CHECK(!state.is_used(1));
    BOOST_CHECK(!state.is_used(2));
}

/**
 * Rolling back to an empty snapshot removes every later mark.
 */
BOOST_AUTO_TEST_CASE(rollback_to_empty_snapshot) {
    FilterState state(3);

    const FilterStateSnapshot empty_snapshot =
        state.snapshot();

    state.mark_used(0);
    state.mark_used(2);

    state.rollback(empty_snapshot);

    for (
        std::size_t filter_index = 0;
        filter_index < 3;
        ++filter_index
    ) {
        BOOST_CHECK(
            !state.is_used(filter_index)
        );
    }
}

/**
 * A state can be reused after rollback.
 */
BOOST_AUTO_TEST_CASE(state_can_be_marked_again_after_rollback) {
    FilterState state(3);

    const FilterStateSnapshot empty_snapshot =
        state.snapshot();

    state.mark_used(0);
    state.mark_used(1);

    state.rollback(empty_snapshot);
    state.mark_used(2);

    BOOST_CHECK(!state.is_used(0));
    BOOST_CHECK(!state.is_used(1));
    BOOST_CHECK(state.is_used(2));
}

BOOST_AUTO_TEST_SUITE_END()
