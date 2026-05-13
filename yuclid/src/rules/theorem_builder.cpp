#include "rules/theorem_builder.hpp"
#include "rules/rule_schema.hpp"
#include "rules/rule_mapping.hpp"
#include "statement/statement.hpp"
#include "theorem.hpp"
#include "statement/statement_builder.hpp"

namespace Yuclid {

    Theorem build_theorem_from_rule_schema(
        const RuleSchema &schema,
        const RuleMapping &mapping
    ) {
        std::vector<std::unique_ptr<Statement>> hypothesis;
        std::vector<std::unique_ptr<Statement>> conclusions;

        hypothesis.reserve(schema.hypotheses.size());
        conclusions.reserve(schema.conclusions.size());

        for(const auto &pattern : schema.hypotheses) {
            hypothesis.push_back(build_statement_from_pattern(pattern, mapping));
        }

        for(const auto &pattern : schema.conclusions) {
            conclusions.push_back(build_statement_from_pattern(pattern, mapping));
        }

        //RuleSchema doesn't have a dedicated display name, so we use the schema id for that
        return Theorem::from_statements(
            schema.id,
            schema.id,
            std::move(hypothesis),
            std::move(conclusions)
        );
    }

}
