#include <cstddef>
#include <format>
#include <stdexcept>
#include <string>

#include "rules/rule_mapping.hpp"
#include "rules/rule_schema.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/equal_angles.hpp"
#include "statement/equal_line_angles.hpp"
#include "statement/para.hpp"
#include "statement/perp.hpp"
#include "statement/statement.hpp"
#include "type/angle.hpp"
#include "type/dist.hpp"

namespace Yuclid {
namespace {

    void check_arity(const RulePredicatePattern &pattern, std::size_t expected) {
        if(pattern.args.size() != expected) {
            throw std::runtime_error(
                std::format("Predicate '{}' expects {} arguments, but got {}",
                    pattern.name,
                    expected,
                    pattern.args.size()
                    )
                );
        }
    }

    Point mapped_point(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t index
    ) {
        const std::string &variable = pattern.args.at(index);

        RuleMapping::const_iterator iterator = mapping.find(variable);
        if(iterator == mapping.end()) {
            throw std::runtime_error(
                std::format(
                    "Predicate {} uses variable {}, but it is missing from rule mapping.",
                    pattern.name,
                    variable
                )
            );
        }

        return iterator->second;
    }
    
    Dist mapped_dist(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t first,
        std::size_t second
    ) {
        return Dist(
            mapped_point(pattern, mapping, first),
            mapped_point(pattern, mapping, second)
        );
    }

    Angle mapped_angle(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t first,
        std::size_t second,
        std::size_t third
    ) {
        return Angle(
            mapped_point(pattern, mapping, first),
            mapped_point(pattern, mapping, second),
            mapped_point(pattern, mapping, third)
        );
    }

    SlopeAngle mapped_slope_angle(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t first,
        std::size_t second
    ) {
        return SlopeAngle(
            mapped_point(pattern, mapping, first),
            mapped_point(pattern, mapping, second)
        );
    }

}
    std::unique_ptr<Statement> build_statement_from_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping
    ) {
        if(pattern.name == "cong") {
            check_arity(pattern, 4);

            return std::make_unique<DistEqDist>(
                mapped_dist(pattern, mapping, 0, 1),
                mapped_dist(pattern, mapping, 2, 3)
            );
        }

        if(pattern.name == "coll") {
            check_arity(pattern, 3);

            return std::make_unique<Collinear>(
                mapped_point(pattern, mapping, 0),
                mapped_point(pattern, mapping, 1),
                mapped_point(pattern, mapping, 2)
            );
        }

        if(pattern.name == "eqangle" || pattern.name == "equal_angles") {
            if(pattern.args.size() == 6) {
                return std::make_unique<EqualAngles>(
                    mapped_angle(pattern, mapping, 0, 1, 2),
                    mapped_angle(pattern, mapping, 3, 4, 5)
                );
            }

            else if(pattern.args.size() == 8) {
                return std::make_unique<EqualLineAngles>(
                    mapped_slope_angle(pattern, mapping, 0, 1),
                    mapped_slope_angle(pattern, mapping, 2, 3),
                    mapped_slope_angle(pattern, mapping, 4, 5),
                    mapped_slope_angle(pattern, mapping, 6, 7)
                );
            }

            throw std::runtime_error(
                std::format(
                    "Predicate '{}' expected either 6 or 8 arguments, but got only {}",
                    pattern.name,
                    pattern.args.size()
                )
            );
        }

        if(pattern.name == "para") {
            check_arity(pattern, 4);

            return std::make_unique<Parallel>(
                mapped_slope_angle(pattern, mapping, 0, 1),
                mapped_slope_angle(pattern, mapping, 2, 3)
            );
        }

        if(pattern.name == "perp") {
            check_arity(pattern, 4);

            return std::make_unique<Perpendicular>(
                mapped_slope_angle(pattern, mapping, 0, 1),
                mapped_slope_angle(pattern, mapping, 2, 3)
            );
        }

        throw std::runtime_error(
            std::format("Unknown rule predicate '{}'", pattern.name)
        );
    }
}
