#include "rule_parser.hpp"
#include <iostream>
#include <sstream>
#include <iosfwd>

namespace Yuclid {

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

    void add_current_rule(
        std::optional<RuleSchema> &currentRule,
        std::vector<RuleSchema> &rules
    ) {
        if(!currentRule.has_value()) {
            return;
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

    std::vector<RuleSchema> parse_rule_schemas(std::istream &input) {
        std::vector<RuleSchema> rules;
        std::optional<RuleSchema> currentRule;

        std::string line;

        while (getline(input, line)) {
            if (line.empty()) {
                continue;
            }

            std::istringstream stream(line);

            std::string action;

            if(!(stream >> action)) {
                continue;
            }

            if(action == "rule") {
                add_current_rule(currentRule, rules);

                RuleSchema rule;

                if(!(stream >> rule.id)) {
                    throw std::runtime_error("Rule is missing an id");
                }
                
                std::string variable;
                while(stream >> variable) {
                    rule.variables.push_back(variable);
                }

                if(rule.variables.empty()) {
                    throw std::runtime_error("Rule has no variables: " + rule.id);
                }

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

            throw std::runtime_error("Unknown rule parser action: " + action);
        }

        add_current_rule(currentRule, rules);

        return rules;
    }
};
