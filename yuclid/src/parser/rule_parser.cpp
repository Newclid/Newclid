#include "rule_parser.hpp"

#include <istream>
#include <sstream>
#include <optional>
#include <string>
#include <utility>
#include <vector>
#include <unordered_set>

namespace Yuclid {
    

    /**
     * @brief Parse rule variables by also checking for uniqueness
     */
    std::vector<std::string> parse_unique_variables(
        std::istream &stream,
        const std::string &rule_id
    ) {
        std::vector<std::string> variables;
        std::unordered_set<std::string> seen_variables;

        std::string variable;
        while(stream >> variable) {
            // insert function returns <iterator, bool> where bool is whether it was successful
            if(!seen_variables.insert(variable).second) {
                throw std::runtime_error(
                    "Duplicate variable '" + variable + "' in rule: " + rule_id
                );
            }

            variables.push_back(variable);
        }

        if(variables.empty()) {
            throw std::runtime_error("Rule has no variables: " + rule_id);
        }

        return variables;
    }

    /**
     * @brief Parses the provided stream to a rule predicate
     */
    RulePredicatePattern parse_rule_predicate(std::istream &stream) {
        RulePredicatePattern pattern;

        if(!(stream >> pattern.name)) {
            throw std::runtime_error("Expected rule predicate name");
        }

        std::string arg;

        while(stream >> arg) {
            pattern.args.push_back(arg);
        }

        if(pattern.args.empty()) {
            throw std::runtime_error("Rule predicate has no arguments: " + pattern.name);
        }

        return pattern;
    }

    /**
     * @brief Checks if the currentRule is a valid one and adds it to all found rules
     */
    void add_current_rule(
        std::optional<RuleSchema> &currentRule,
        std::vector<RuleSchema> &rules
    ) {
        if(!currentRule.has_value()) {
            throw std::runtime_error("Found 'end' before defining a rule");
        }

        if(currentRule->hypotheses.empty()) {
            throw std::runtime_error("Rule has no premises: " + currentRule->id);
        }

        if(currentRule->conclusions.empty()) {
            throw std::runtime_error("Rule has no conclusions: " + currentRule->id);
        }

        rules.push_back(std::move(*currentRule));
        currentRule.reset();
    }

    /**
     * @brief Parses the input stream to a list of Rule schemas
     * 
     * Format
     *      rule <rule_id> <variables...>
     *      require <predicate_name> <arguments...>
     *      conclude <predicate_name> <arguments...>
     *      end
     *
     */
    std::vector<RuleSchema> parse_rule_schemas(std::istream &input) {
        std::vector<RuleSchema> rules;
        std::optional<RuleSchema> currentRule;

        std::string line;

        while (std::getline(input, line)) {
            if (line.empty()) {
                continue;
            }

            std::istringstream stream(line);

            std::string action;

            if(!(stream >> action)) {
                continue;
            }

            if(action == "rule") {

                if(currentRule.has_value()) {
                    throw std::runtime_error(
                        "Found new rule before closing previous rule with 'end': "
                        + currentRule->id
                    );
                }

                RuleSchema rule;

                if(!(stream >> rule.id)) {
                    throw std::runtime_error("Rule is missing an id");
                }
                
                rule.variables = parse_unique_variables(stream, rule.id);

                currentRule = std::move(rule);
                continue;
            }

            if(action == "require") {
                if(!currentRule.has_value()) {
                    throw std::runtime_error("Found 'require' before defining a rule");
                }

                currentRule->hypotheses.push_back(parse_rule_predicate(stream));
                continue;
            }

            if(action == "conclude") {
                if(!currentRule.has_value()) {
                    throw std::runtime_error("Found 'conclude' before defining a rule");
                }

                currentRule->conclusions.push_back(parse_rule_predicate(stream));
                continue;
            }

            if(action == "end") {
                add_current_rule(currentRule, rules);
                continue;
            }

            throw std::runtime_error("Unknown rule parser action: " + action);
        }
        
        if(currentRule.has_value()) {
            throw std::runtime_error("Rule is missing 'end': " + currentRule->id);
        }

        return rules;
    }
} // namespace Yuclid
