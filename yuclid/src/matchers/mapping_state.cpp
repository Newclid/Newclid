#include "matchers/mapping_state.hpp"

#include <cassert>
#include <stdexcept>

#include "problem.hpp"

namespace Yuclid {
    void MappingExtension::add_assignment(
        RuleVariableIndex variable_idx,
        ProblemPointIndex point_idx
    ) {
        m_assignments.push_back({
            variable_idx,
            point_idx
        });
    }

    void MappingExtension::add_assignment(
        RuleVariableIndex variable_idx,
        Point point
    ) {
        add_assignment(variable_idx, point.get());
    }

    const std::vector<MappingAssignment> &MappingExtension::assignments() const {
        return m_assignments;
    }

    bool MappingExtension::empty() const {
        return m_assignments.empty();
    }

    MappingState::MappingState(
        const RuleSchema &schema,
        const Problem &problem
    )
        :m_schema(&schema),
         m_problem(&problem),
         m_point_by_variable(schema.variables.size(), UNASSIGNED_POINT),
         m_used_points(problem.num_points(), 0)
    {
        if (schema.variables.size() > 64) {
            throw std::invalid_argument("MappingState supports at most 64 rule variables");
        }
    }

    std::uint64_t MappingState::bit_for(
        RuleVariableIndex variable_idx
    ) const {
        assert(variable_idx < 64);

        return std::uint64_t{1} << variable_idx;
    }

    bool MappingState::is_rule_variable(
        RuleVariableIndex variable_idx
    ) const {
        return variable_idx < m_schema->variables.size();
    }

    bool MappingState::is_assigned(
        RuleVariableIndex variable_idx
    ) const {
        if(!is_rule_variable(variable_idx)) {
            return false;
        }

        return (m_assigned_variables & bit_for(variable_idx)) != 0;
    }

    std::optional<ProblemPointIndex> MappingState::assigned_point_index(
        RuleVariableIndex variable_idx
    ) const {
        if(!is_rule_variable(variable_idx)) return std::nullopt;
        if(!is_assigned(variable_idx)) return std::nullopt;

        return m_point_by_variable[variable_idx];
    }

    bool MappingState::is_point_used(
        ProblemPointIndex point_idx
    ) const {
        if(point_idx >= m_used_points.size()) return false;

        return m_used_points[point_idx] != 0;
    }

    bool MappingState::is_point_used(
        Point point
    ) const {
        return is_point_used(point.get());
    }

    std::size_t MappingState::assigned_count() const {
        return m_assigned_count;
    }

    bool MappingState::is_complete() const {
        return m_assigned_count == m_schema->variables.size();
    }

    std::vector<RuleVariableIndex> MappingState::unassigned_variables() const {
        std::vector<RuleVariableIndex> result;
        result.reserve(m_schema->variables.size());

        for(RuleVariableIndex curr = 0; curr < m_schema->variables.size(); curr++) {
            if(!is_assigned(curr)) result.push_back(curr);
        }

        return result;
    }

    MappingStateSnapshot MappingState::snapshot() const {
        return {
            .assigned_variables=m_assigned_variables,
            .assigned_count=m_assigned_count
        };
    }

    void MappingState::rollback(
        MappingStateSnapshot snapshot
    ) {
        const std::uint64_t newly_assigned =
            m_assigned_variables & ~snapshot.assigned_variables;

        for(RuleVariableIndex curr_idx = 0; curr_idx < m_schema->variables.size(); curr_idx++) {
            if((newly_assigned & bit_for(curr_idx)) == 0) continue;

            const ProblemPointIndex point_idx = m_point_by_variable[curr_idx];

            m_used_points[point_idx] = 0;
            m_point_by_variable[curr_idx] = UNASSIGNED_POINT;
        }
        
        m_assigned_variables = snapshot.assigned_variables;
        m_assigned_count = snapshot.assigned_count;
    }

    bool MappingState::try_apply_assignment(
        RuleVariableIndex variable_idx,
        ProblemPointIndex point_idx
    ) {
        if(!is_rule_variable(variable_idx)) return false;
        if(point_idx >= m_used_points.size()) return false;

        if(is_assigned(variable_idx)) {
            return m_point_by_variable[variable_idx] == point_idx;
        }

        if(is_point_used(point_idx)) return false;

        m_point_by_variable[variable_idx] = point_idx;
        m_used_points[point_idx] = 1;
        m_assigned_variables |= bit_for(variable_idx);
        ++m_assigned_count;

        return true;
    }

    bool MappingState::try_apply_assignment(
        RuleVariableIndex variable_idx,
        Point point
    ) {
        return try_apply_assignment(variable_idx, point.get());
    }

    bool MappingState::try_apply_assignment(
        const MappingAssignment &assignment
    ) {
        return try_apply_assignment(
            assignment.variable_idx,
            assignment.point_idx
        );
    }

    bool MappingState::try_apply_extension(
        const MappingExtension &extension
    ) {
        MappingStateSnapshot before = snapshot();

        for(const MappingAssignment &assignment : extension.assignments()) {
            if(!try_apply_assignment(assignment)) {
                rollback(before);

                return false;
            }
        }

        return true;
    }

    std::optional<RuleMapping> MappingState::to_rule_mapping() const {
        if (!is_complete()) {
            return std::nullopt;
        }

        RuleMapping rule_mapping;
        
        for(RuleVariableIndex curr_idx = 0; curr_idx < m_schema->variables.size(); curr_idx++) {
            const ProblemPointIndex point_idx = m_point_by_variable[curr_idx];
            
            assert(point_idx != UNASSIGNED_POINT);
            assert(point_idx < m_used_points.size());

            const std::string &variable_name = m_schema->variables[curr_idx];

            rule_mapping.emplace(
                variable_name,
                Point(point_idx, m_problem)
            );
        }

        return rule_mapping;
    }
}
