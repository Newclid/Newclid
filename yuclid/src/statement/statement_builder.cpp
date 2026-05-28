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
#include "statement/eqratio.hpp"
#include "statement/cyclic.hpp"
#include "statement/circumcenter.hpp"
#include "statement/similar_triangles.hpp"
#include "statement/congruent_triangles.hpp"
#include "statement/midpoint.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "statement/dist_eq.hpp"
#include "statement/squared_dist_eq.hpp"
#include "statement/same_clock.hpp"
#include "statement/obtuse_angle.hpp"
#include "statement/same_side.hpp"
#include "statement/diff_side.hpp"
#include "statement/line_angle_eq.hpp"
#include "statement/statement.hpp"
#include "type/angle.hpp"
#include "type/dist.hpp"
#include "type/point.hpp"
#include "type/slope_angle.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"

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

    SquaredDist mapped_squared_dist(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t first,
        std::size_t second
    ) {
        return SquaredDist(
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

    Triangle mapped_triangle(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::size_t first,
        std::size_t second,
        std::size_t third
    ) {
        return Triangle(
            mapped_point(pattern, mapping, first),
            mapped_point(pattern, mapping, second),
            mapped_point(pattern, mapping, third)
        );
    }

    template <typename ExpectedConstType>
    ExpectedConstType parsed_constant(
        const RulePredicatePattern &pattern,
        std::size_t index
    ) {
        static_assert(
            std::is_same_v<ExpectedConstType, NNRat> || std::is_same_v<ExpectedConstType, Rat>,
            "parsed_constant can only be used with NNRat or Rat!"
        );

        const std::string &value_str = pattern.args.at(index);

        try {
            // Check if it's a fraction "a/b"
            std::size_t slash_pos = value_str.find('/');
            
            if (slash_pos != std::string::npos) {
                // std::stoll will also convert hexadecimals (0xffff and 0f0) to decimals
                long long num = std::stoll(value_str.substr(0, slash_pos));
                long long den = std::stoll(value_str.substr(slash_pos + 1));
                return ExpectedConstType(num, den);
            } else {
                long long num = std::stoll(value_str);
                return ExpectedConstType(num);
            }
        } catch (const std::exception&) {
            throw std::runtime_error(
                std::format("Predicate '{}' expected a valid fraction or integer at index {}, but got '{}'",
                            pattern.name, index, value_str)
            );
        }
    }

    void build_coll_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::vector<std::unique_ptr<Statement>> &results
    ) {
        if(pattern.args.size() < 3) check_arity(pattern, 3);
        
        for(std::size_t i = 2; i < pattern.args.size(); ++i){
            results.push_back(
                std::make_unique<Collinear>(
                    mapped_point(pattern, mapping, i - 2),
                    mapped_point(pattern, mapping, i - 1),
                    mapped_point(pattern, mapping, i)
                )
            );
        }
    }

    void build_cyclic_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::vector<std::unique_ptr<Statement>> &results
    ) {
        if(pattern.args.size() < 4) check_arity(pattern, 4);

        for(std::size_t i = 3; i < pattern.args.size(); ++i){
            results.push_back(
                std::make_unique<CyclicQuadrangle>(
                    mapped_point(pattern, mapping, i - 3),
                    mapped_point(pattern, mapping, i - 2),
                    mapped_point(pattern, mapping, i - 1),
                    mapped_point(pattern, mapping, i)
                )
            );
        }
    }

    void build_circumcenter_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping,
        std::vector<std::unique_ptr<Statement>> &results
    ) {
        if(pattern.args.size() < 4) check_arity(pattern, 4);
        
        Point center = mapped_point(pattern, mapping, 0);

        for(std::size_t i = 3; i < pattern.args.size(); ++i){
            results.push_back(
                std::make_unique<Circumcenter>(
                    center,
                    mapped_triangle(pattern, mapping, i - 2, i - 1, i)
                )
            );
        }
    }

}
    std::vector<std::unique_ptr<Statement>> build_statements_from_pattern(
        const RulePredicatePattern &pattern,
        const RuleMapping &mapping
    ) {
        std::vector<std::unique_ptr<Statement>> statements;

        if(pattern.name == "cong") {
            check_arity(pattern, 4);

            statements.push_back(
                std::make_unique<DistEqDist>(
                    mapped_dist(pattern, mapping, 0, 1),
                    mapped_dist(pattern, mapping, 2, 3)
            ));
            return statements;
        }
        
        if(pattern.name == "coll") {
            build_coll_pattern(pattern, mapping, statements);
            return statements;
        }

        if(pattern.name == "eqangle" || pattern.name == "equal_angles") {
            if(pattern.args.size() == 6) {
                statements.push_back(std::make_unique<EqualAngles>(
                    mapped_angle(pattern, mapping, 0, 1, 2),
                    mapped_angle(pattern, mapping, 3, 4, 5)
                ));
                return statements;
            }

            else if(pattern.args.size() == 8) {
                statements.push_back(std::make_unique<EqualLineAngles>(
                    mapped_slope_angle(pattern, mapping, 0, 1),
                    mapped_slope_angle(pattern, mapping, 2, 3),
                    mapped_slope_angle(pattern, mapping, 4, 5),
                    mapped_slope_angle(pattern, mapping, 6, 7)
                ));
                return statements;
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

            statements.push_back(std::make_unique<Parallel>(
                mapped_slope_angle(pattern, mapping, 0, 1),
                mapped_slope_angle(pattern, mapping, 2, 3)
            ));
            return statements;
        }

        if(pattern.name == "perp") {
            check_arity(pattern, 4);

            statements.push_back(std::make_unique<Perpendicular>(
                mapped_slope_angle(pattern, mapping, 0, 1),
                mapped_slope_angle(pattern, mapping, 2, 3)
            ));
            return statements;
        }

        if(pattern.name == "eqratio") {
            check_arity(pattern, 8);

            statements.push_back(std::make_unique<EqualRatios>(
                mapped_dist(pattern, mapping, 0, 1),
                mapped_dist(pattern, mapping, 2, 3),
                mapped_dist(pattern, mapping, 4, 5),
                mapped_dist(pattern, mapping, 6, 7)
            ));
            return statements;
        }

        if(pattern.name == "cyclic") {
            build_cyclic_pattern(pattern, mapping, statements);
            return statements;
        }

        if(pattern.name == "circumcenter" || pattern.name == "circle") {
            build_circumcenter_pattern(pattern, mapping, statements);
            return statements;
        }

        if(pattern.name == "simtri") {
            check_arity(pattern, 6);
 
            statements.push_back(std::make_unique<SimilarTriangles>(
                mapped_triangle(pattern, mapping, 0, 1, 2),
                mapped_triangle(pattern, mapping, 3, 4, 5),
                true
            ));
            return statements;
        }

        if(pattern.name == "simtrir") {
            check_arity(pattern, 6);
 
            statements.push_back(std::make_unique<SimilarTriangles>(
                mapped_triangle(pattern, mapping, 0, 1, 2),
                mapped_triangle(pattern, mapping, 3, 4, 5),
                false
            ));
            return statements;
        }

        if(pattern.name == "contri") {
            check_arity(pattern, 6);
 
            statements.push_back(std::make_unique<CongruentTriangles>(
                mapped_triangle(pattern, mapping, 0, 1, 2),
                mapped_triangle(pattern, mapping, 3, 4, 5),
                true
            ));
            return statements;
        }

        if(pattern.name == "contrir") {
            check_arity(pattern, 6);
 
            statements.push_back(std::make_unique<CongruentTriangles>(
                mapped_triangle(pattern, mapping, 0, 1, 2),
                mapped_triangle(pattern, mapping, 3, 4, 5),
                false
            ));
            return statements;
        }

        if(pattern.name == "midp") {
            check_arity(pattern, 3);
 
            statements.push_back(std::make_unique<Midpoint>(
                mapped_point(pattern, mapping, 0),
                mapped_point(pattern, mapping, 1),
                mapped_point(pattern, mapping, 2)
            ));
            return statements;
        }

        if(pattern.name == "rconst") {
            check_arity(pattern, 5);

            statements.push_back(std::make_unique<RatioDistEquals>(
                mapped_dist(pattern, mapping, 0, 1),
                mapped_dist(pattern, mapping, 2, 3),
                parsed_constant<NNRat>(pattern, 4)
            ));
            return statements;
        }

        if(pattern.name == "r2const") {
            check_arity(pattern, 5);

            statements.push_back(std::make_unique<RatioSquaredDist>(
                mapped_squared_dist(pattern, mapping, 0, 1),
                mapped_squared_dist(pattern, mapping, 2, 3),
                parsed_constant<NNRat>(pattern, 4)
            ));
            return statements;
        }

        if(pattern.name == "lconst") {
            check_arity(pattern, 3);

            statements.push_back(std::make_unique<DistEq>(
                mapped_dist(pattern, mapping, 0, 1),
                parsed_constant<NNRat>(pattern, 2)
            ));
            return statements;
        }

        if(pattern.name == "l2const") {
            check_arity(pattern, 3);

            statements.push_back(std::make_unique<SquaredDistEq>(
                mapped_squared_dist(pattern, mapping, 0, 1),
                parsed_constant<NNRat>(pattern, 2)
            ));
            return statements;
        }
        
        if(pattern.name == "aconst") {
            check_arity(pattern, 5);

            statements.push_back(LineAngleEq(
                mapped_slope_angle(pattern, mapping, 0, 1),
                mapped_slope_angle(pattern, mapping, 2, 3),
                parsed_constant<Rat>(pattern, 4)
            ).normalize());
            return statements;
        }

        if(pattern.name == "sameclock") {
            check_arity(pattern, 6);

            statements.push_back(std::make_unique<SameClock>(
                mapped_triangle(pattern, mapping, 0, 1, 2),
                mapped_triangle(pattern, mapping, 3, 4, 5)
            ));
            return statements;
        }

        if(pattern.name == "obtuse_angle") {
            check_arity(pattern, 3);

            statements.push_back(std::make_unique<ObtuseAngle>(
                mapped_angle(pattern, mapping, 0, 1, 2)
            ));
            return statements;
        }

        if(pattern.name == "sameside") {
            check_arity(pattern, 6);

            statements.push_back(std::make_unique<SameSignDot>(
                mapped_point(pattern, mapping, 0),
                mapped_point(pattern, mapping, 1),
                mapped_point(pattern, mapping, 2),
                mapped_point(pattern, mapping, 3),
                mapped_point(pattern, mapping, 4),
                mapped_point(pattern, mapping, 5)
            ));
            return statements;
        } 
        
        if(pattern.name == "nsameside") {
            check_arity(pattern, 6);

            statements.push_back(std::make_unique<DiffSignDot>(
                mapped_point(pattern, mapping, 0),
                mapped_point(pattern, mapping, 1),
                mapped_point(pattern, mapping, 2),
                mapped_point(pattern, mapping, 3),
                mapped_point(pattern, mapping, 4),
                mapped_point(pattern, mapping, 5)
            ));
            return statements;
        }

        throw std::runtime_error(
            std::format("Unknown rule predicate '{}'", pattern.name)
        );
    }
}
