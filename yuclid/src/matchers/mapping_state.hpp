#pragma once

#include <cstddef>
#include <optional>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "type/point.hpp"

namespace Yuclid {
    struct MappingAssignment {
        std::string variable;
        Point point;
    };

    class MappingExtension {
    public:
        void add_assignment(
            std::string variable,
            Point point
        );

        [[nodiscard]] const std::vector<MappingAssignment> &assignments() const;

        [[nodiscard]] bool empty() const;

    private:
        std::vector<MappingAssignment> m_assignments;
    };

    /**
     * One partial mapping from rule variables to problem points.
     *
     * Example:
     *   A -> P1
     *   B -> P3
     *   C -> unassigned
     *
     * This class enforces:
     *   - unknown rule variables cannot be assigned
     *   - one rule variable cannot map to two different points
     *   - two different rule variables cannot map to the same point
     *   - incomplete states cannot be converted to RuleMapping
     */
    class MappingState {
    public:
        explicit MappingState(
            const RuleSchema &schema
        );

        explicit MappingState(
            std::vector<std::string> rule_variables
        );

        [[nodiscard]] bool is_rule_variable(
            const std::string &variable
        ) const;

        [[nodiscard]] bool is_assigned(
            const std::string &variable
        ) const;

        [[nodiscard]] std::optional<Point> assigned_point(
            const std::string &variable
        ) const;

        [[nodiscard]] bool is_point_used(
            Point point
        ) const;

        /**
         * Try to add one variable -> point assignment.
         *
         * Returns a new MappingState if compatible.
         * Returns std::nullopt if the assignment conflicts.
         */
        [[nodiscard]] std::optional<MappingState> with_assignment(
            const std::string &variable,
            Point point
        ) const;

        /**
         * Try to apply several assignments at once.
         *
         * Returns a new MappingState if all assignments are compatible.
         * Returns std::nullopt if any assignment conflicts.
         */
        [[nodiscard]] std::optional<MappingState> merged_with(
            const MappingExtension &extension
        ) const;

        [[nodiscard]] bool is_complete() const;

        [[nodiscard]] std::vector<std::string> unassigned_variables() const;

        [[nodiscard]] std::optional<RuleMapping> to_rule_mapping() const;

    private:
        std::vector<std::string> m_rule_variables;
        std::unordered_map<std::string, std::optional<Point>> m_mapping;
        std::unordered_set<std::size_t> m_used_point_indices;
        std::size_t m_assigned_count = 0;
    };
}
