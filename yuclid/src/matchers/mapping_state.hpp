#pragma once

#include <cstddef>
#include <optional>
#include <cstdint>
#include <limits>
#include <vector>

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "type/point.hpp"

namespace Yuclid {
    using RuleVariableIndex = std::size_t;
    using ProblemPointIndex = std::size_t;

    /**
     * Sentinel value used in m_point_by_variable to mark that a rule variable
     * is currently not assigned to any problem point.
     */
    static constexpr ProblemPointIndex UNASSIGNED_POINT =
        std::numeric_limits<ProblemPointIndex>::max();

    /**
     * One assignment inside a mapping extension.
     *
     * Both values are indices:
     *   - variable_idx: index into RuleSchema::variables
     *   - point_idx: index of a concrete point in the problem
     *
     * Example:
     *   RuleSchema::variables = ["A", "B", "C"]
     *   MappingAssignment{1, 5} means B -> problem point 5
     */
    struct MappingAssignment {
        RuleVariableIndex variable_idx;
        ProblemPointIndex point_idx;
    };

    /**
     * A small batch of assignments that can be applied to a MappingState.
     *
     * Predicate providers should generate MappingExtensions using integer indices,
     * not strings, so the DFS search does not repeatedly hash variable names.
     */
    class MappingExtension {
    public:
        void add_assignment(
            RuleVariableIndex variable_idx,
            ProblemPointIndex point_idx
        );

        void add_assignment(
            RuleVariableIndex variable_idx,
            Point point
        );

        [[nodiscard]] const std::vector<MappingAssignment> &assignments() const;

        [[nodiscard]] bool empty() const;

    private:
        std::vector<MappingAssignment> m_assignments;
    };

    /**
     * Snapshot of the mutable mapping state.
     *
     * Rollback is cheap because the assigned rule variables are stored as a bitmask.
     */
    struct MappingStateSnapshot {
        std::uint64_t assigned_variables;
        std::size_t assigned_count;
    };
    
    /**
     * Mutable partial mapping from rule variables to concrete problem points.
     *
     * Rule variables are represented by their index in RuleSchema::variables.
     * Problem points are represented by their point index.
     *
     * Example:
     *   RuleSchema::variables = ["A", "B", "C", "D"]
     *
     *   variable index:
     *      A -> 0
     *      B -> 1
     *      C -> 2
     *      D -> 3
     *
     *   partial mapping:
     *      A -> point 5
     *      B -> unassigned
     *      C -> point 8
     *      D -> unassigned
     *
     *   m_assigned_variables:
     *      bit 0 = 1  because A is assigned
     *      bit 1 = 0  because B is unassigned
     *      bit 2 = 1  because C is assigned
     *      bit 3 = 0  because D is unassigned
     *
     *   So the bitmask is conceptually:
     *      0101
     *
     */
    class MappingState {
    public:
        explicit MappingState(
            const RuleSchema &schema,
            const Problem &problem
        );

        [[nodiscard]] bool is_rule_variable(
            RuleVariableIndex variable_idx
        ) const;

        [[nodiscard]] bool is_assigned(
            RuleVariableIndex variable_idx
        ) const;

        [[nodiscard]] std::optional<ProblemPointIndex> assigned_point_index(
            RuleVariableIndex variable_idx
        ) const;

        [[nodiscard]] bool is_point_used(
            ProblemPointIndex point_idx
        ) const;

        [[nodiscard]] bool is_point_used(
            Point point
        ) const;

        [[nodiscard]] std::size_t assigned_count() const;

        [[nodiscard]] bool is_complete() const;

        [[nodiscard]] std::vector<RuleVariableIndex> unassigned_variables() const;

        MappingStateSnapshot snapshot() const;

        void rollback(
            MappingStateSnapshot snapshot
        );

        [[nodiscard]] bool try_apply_assignment(
            RuleVariableIndex variable_idx,
            ProblemPointIndex point_idx
        );

        [[nodiscard]] bool try_apply_assignment(
            RuleVariableIndex variable_idx,
            Point point
        );

        [[nodiscard]] bool try_apply_assignment(
            const MappingAssignment &assignment
        );

        [[nodiscard]] bool try_apply_extension(
            const MappingExtension &extension
        );

        [[nodiscard]] std::optional<RuleMapping> to_rule_mapping() const;

        [[nodiscard]] RuleMapping to_partial_rule_mapping() const;

    private:
        /**
         * Bit for variable_idx in m_assigned_variables.
         * Example: 0 -> 0001, 1 -> 0010, 2 -> 0100.
         */
        [[nodiscard]] std::uint64_t bit_for(
            RuleVariableIndex variable_idx
        ) const;

        const RuleSchema *m_schema;
        const Problem *m_problem;

        /**
         * variable_idx -> assigned problem point index.
         * UNASSIGNED_POINT means the variable is not mapped yet.
         *
         * Example:
         *   variables = ["A", "B", "C"]
         *   [5, UNASSIGNED_POINT, 8] means A -> 5, B unassigned, C -> 8.
         */
        std::vector<ProblemPointIndex> m_point_by_variable;

        /**
         * point_idx -> whether this concrete problem point is already used.
         * Uses unsigned char instead of vector<bool> for normal array access.
         */
        std::vector<unsigned char> m_used_points;

        /**
         * Bitmask of assigned rule variables.
         * Bit i corresponds to m_schema->variables[i].
         *
         * Example:
         *   variables = ["A", "B", "C", "D"]
         *   A and C assigned -> 0101.
         *
         * Supports at most 64 rule variables.
         */
        std::uint64_t m_assigned_variables = 0;

        /**
         * Number of assigned rule variables.
         * Used for fast is_complete().
         */
        std::size_t m_assigned_count = 0;
    };
}
