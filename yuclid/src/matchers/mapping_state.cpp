
#include "matchers/mapping_state.hpp"
#include "rules/rule_schema.hpp"
namespace Yuclid {

    void MappingExtension::add_assignment(
        std::string variable,
        Point point
    ) {
        m_assignments.push_back(MappingAssignment {
            .variable = std::move(variable),
            .point = point
        });
    }

    const std::vector<MappingAssignment> &MappingExtension::assignments() const {
        return m_assignments;
    }

    bool MappingExtension::empty() const {
        return m_assignments.empty();
    }
    
    MappingState::MappingState(
        const RuleSchema &schema
    ) : MappingState(schema.variables) {}

    MappingState::MappingState(
        std::vector<std::string> rule_variables
    ) : m_rule_variables(std::move(rule_variables))
    {
        for(const std::string &variable : m_rule_variables) {
            m_mapping.emplace(variable, std::nullopt);
        }
    }

    bool MappingState::is_rule_variable(
        const std::string &variable
    ) const {
        return m_mapping.contains(variable);
    }

    bool MappingState::is_assigned(
        const std::string &variable
    ) const {
        const auto it = m_mapping.find(variable);

        if(it == m_mapping.end()) {
            return false;
        }

        return it->second.has_value();
    }

    std::optional<Point> MappingState::assigned_point(
        const std::string &variable
    ) const {
        const auto it = m_mapping.find(variable);

        if(it == m_mapping.end()) {
            return std::nullopt;
        }

        return it->second;
    }
    
    bool MappingState::is_point_used(
        Point point
    ) const {
        return m_used_point_indices.contains(point.get());
    }

    bool MappingState::is_complete() const {
        return m_assigned_count == m_rule_variables.size();
    }

    std::vector<std::string> MappingState::unassigned_variables() const {
        std::vector<std::string> variables;

        for(const std::string &variable : m_rule_variables) {
            if(!m_mapping.at(variable).has_value()) {
                variables.push_back(variable);
            }
        }

        return variables;
    }

    std::optional<RuleMapping> MappingState::to_rule_mapping() const {
        if(!is_complete()) {
            return std::nullopt;
        }

        RuleMapping rule_mapping;
            
        for(const std::string &variable : m_rule_variables) {
            const std::optional<Point> &point = m_mapping.at(variable);

            rule_mapping.emplace(variable, point.value());
        }

        return rule_mapping;
    }
}
