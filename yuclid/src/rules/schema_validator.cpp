#include "schema_validator.hpp"
#include <vector>
#include <algorithm>
#include <format>

namespace Yuclid {
    namespace {
        std::optional<std::string> validate_predicate(
            const std::string &schema_id,
            const RulePredicatePattern &pattern,
            const std::vector<std::string> &declared_vars
        ) {
            const std::string &name = pattern.name;
            const std::size_t args_size = pattern.args.size();
            
            // Arity and Existence Check
            bool valid_arity = false;
            std::string expected_msg;
            
            if (name == "cong" || name == "para" || name == "perp") {
                valid_arity = (args_size == 4);
                expected_msg = "exactly 4";
            } 
            else if (name == "coll") {
                valid_arity = (args_size >= 3);
                expected_msg = "at least 3";
            }
            else if (name == "eqangle" || name == "equal_angles") {
                valid_arity = (args_size == 6 || args_size == 8);
                expected_msg = "either 6 or 8";
            }
            else if (name == "eqratio") {
                valid_arity = (args_size == 8);
                expected_msg = "exactly 8";
            }
            else if (name == "cyclic" || name == "circumcenter" || name == "circle") {
                valid_arity = (args_size >= 4);
                expected_msg = "at least 4";
            }
            else if (name == "simtri" || name == "simtrir" || name == "contri" || 
                     name == "contrir" || name == "sameclock" || name == "sameside" || name == "nsameside") {
                valid_arity = (args_size == 6);
                expected_msg = "exactly 6";
            }
            else if (name == "midp" || name == "lconst" || name == "l2const" || name == "obtuse_angle") {
                valid_arity = (args_size == 3);
                expected_msg = "exactly 3";
            }
            else if (name == "rconst" || name == "r2const" || name == "aconst") {
                valid_arity = (args_size == 5);
                expected_msg = "exactly 5";
            }
            else {
                return std::format("Schema '{}' Error: Unknown rule predicate '{}'.", schema_id, name);
            }
            
            if (!valid_arity) {
                return std::format("Schema '{}' Error: Predicate '{}' expects {} arguments, but got {}.", 
                                   schema_id, name, expected_msg, args_size);
            }

            // Check for undefined variables
            for (std::size_t i = 0; i < args_size; ++i) {
                const std::string &arg = pattern.args[i];

                // Skip constant validation for these predicates to maintain legacy compatibility, 
                // for a more detailed explanation, check the parsed_constant() function in StatementBuilder
                if ((name == "rconst" || name == "r2const" || name == "aconst") && i == 4) continue;
                if ((name == "lconst" || name == "l2const") && i == 2) continue;
                
                auto it = std::find(declared_vars.begin(), declared_vars.end(), arg);
                if (it == declared_vars.end()) {
                    return std::format("Schema '{}' Error: Variable '{}' used in '{}' is not declared.", 
                                       schema_id, arg, name);
                }
            }
            return std::nullopt;
        }
    }

    std::optional<std::string> validate_schema(const RuleSchema &schema) {
       for (const auto &hyp : schema.hypotheses) {
            auto err = validate_predicate(schema.id, hyp, schema.variables);
            if (err.has_value()) return err;
        }
        for (const auto &conc : schema.conclusions) {
            auto err = validate_predicate(schema.id, conc, schema.variables);
            if (err.has_value()) return err;
        }
        return std::nullopt;
    }

}