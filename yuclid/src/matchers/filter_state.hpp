#pragma once

#include <cstddef>
#include <cstdint>

namespace Yuclid {
    struct FilterStateSnapshot {
        std::uint64_t passed_filters;
    };

    class FilterState {
    public:
        explicit FilterState(std::size_t filter_count);

        [[nodiscard]] bool is_used(
            std::size_t filter_idx
        ) const;

        void mark_used(
            std::size_t filter_idx
        );

        [[nodiscard]] FilterStateSnapshot snapshot() const;

        void rollback(
            FilterStateSnapshot snapshot
        );

    private:
        [[nodiscard]] std::uint64_t bit_for(
            std::size_t filter_idx
        ) const;

        std::size_t m_filter_count;
        std::uint64_t m_passed_filters = 0;
    };
}
