#include "matchers/filter_state.hpp"
#include <stdexcept>

namespace Yuclid {
    FilterState::FilterState(std::size_t filter_count)
        : m_filter_count(filter_count)
    {
        if (filter_count > 64) {
            throw std::invalid_argument("FilterState supports at most 64 filters");
        }
    }

    std::uint64_t FilterState::bit_for(
        std::size_t filter_idx
    ) const {
        return std::uint64_t{1} << filter_idx;
    }

    bool FilterState::is_used(
        std::size_t filter_idx
    ) const {
        if(filter_idx >= m_filter_count) {
            return false;
        }

        return (m_used_filters & bit_for(filter_idx)) != 0;
    }

    void FilterState::mark_used(
        std::size_t filter_idx
    ) {
        if(filter_idx >= m_filter_count) {
            return;
        }

        m_used_filters |= bit_for(filter_idx);
    }

    FilterStateSnapshot FilterState::snapshot() const {
        return {
            .used_filters=m_used_filters,
        };
    }

    void FilterState::rollback(
        FilterStateSnapshot snapshot
    ) {
        m_used_filters = snapshot.used_filters;
    }
}
