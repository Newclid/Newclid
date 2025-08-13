/**
   Copyright 2025 Concordance Inc. dba Harmonic

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
#include "config_options.hpp" // Include our configuration class header
#include "matcher.hpp"
#include "parser/simple.hpp"
#include "problem.hpp"
#include "statement/statement.hpp"
#include "theorem.hpp"
#include "solver/statement_proof.hpp"
#include "type/squared_dist.hpp"
#include "type/triangle.hpp"
#include "solver/ddar_solver.hpp"
#include "solver/theorem_application.hpp"
#include <boost/json/serialize.hpp>
#include <boost/json/value.hpp>
#include <boost/json/value_from.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/keywords/filter.hpp>
#include <boost/log/keywords/format.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/utility/setup/console.hpp>


#include <format>
#include <iostream>     // For std::cout, std::cerr
#include <fstream>
#include <stdexcept>    // For std::runtime_error
#include <vector>

using namespace std;
using namespace Yuclid;

namespace logging = boost::log;
namespace keywords = boost::log::keywords;

namespace {

  void init_logging(const Config::Global &config)
  {
    logging::add_console_log
      (std::cerr,
       keywords::filter = logging::trivial::severity >= config.log_level(),
       keywords::format = "[%TimeStamp%] [%Severity%] %Message%");

    // Add common attributes, like TimeStamp, LineID etc.
    logging::add_common_attributes();
  }

  bool run_ddar(const Problem &prob, const Config &config) {
    BOOST_LOG_TRIVIAL(info) << "Start initialization";
    DDARSolver solver(&prob, &config.solver());
    BOOST_LOG_TRIVIAL(info) << "Matched " << solver.num_theorems() << " theorems";

    for (const auto &goal : prob.goals()) {
      if (!goal->check_numerically()) {
        BOOST_LOG_TRIVIAL(fatal) << *goal << " failed numerical checks. Aborting.";
        throw runtime_error("Problem's goals failed numerical check");
      }
    }
    BOOST_LOG_TRIVIAL(info) << "Running DD+AR";
    bool const res = solver.run(500);
    if (config.global().use_json()) {
      solver.print_json(cout);
    } else {
      solver.print_proof(cout);
    }
    if (!res) {
      BOOST_LOG_TRIVIAL(info) << "Failed to solve the problem";
    }
    return res;
  }

  void match_theorems(const Problem &prob, const Config &config) {
    TheoremMatcher matcher(&prob, &config.solver());
    BOOST_LOG_TRIVIAL(info) << std::format("Matched {} theorems", matcher.theorems().size());
    if (config.global().use_json()) {
      boost::json::value const jv = boost::json::value_from(matcher.theorems());
      cout << boost::json::serialize(jv) << '\n';
    } else {
      for (const auto &thm : matcher.theorems()) {
        cout << thm << '\n';
      }
    }
  }

  int run_file(const Config &config, istream &input) {
    Problem prob = parse_input_simple(input);

    switch (config.global().mode()) {
    case Config::Mode::DDAR:
      if (!run_ddar(prob, config) && config.global().err_on_failure()) {
        return 2;
      }
      break;
    case Config::Mode::MATCH:
      match_theorems(prob, config);
    }
    return 0;
  }

}

int main(int argc, char* argv[]) {
  try {
    // Step 1: Initialize the static configuration options.
    // This is the first action to perform, as it parses arguments
    // and sets up the entire application's configuration.
    Config config(argc, argv);

    init_logging(config.global());
    BOOST_LOG_TRIVIAL(debug) << "Logging at level " << config.global().log_level();
    BOOST_LOG_TRIVIAL(debug) << "Additive lengths AR table is "
                             << (config.solver().ar_enabled<Dist>() ? "enabled" : "disabled");
    BOOST_LOG_TRIVIAL(debug) << "Additive squared lengths AR table is "
                             << (config.solver().ar_enabled<SquaredDist>() ? "enabled" : "disabled");
    BOOST_LOG_TRIVIAL(debug) << "Equations in theorems are "
                             << (config.solver().eqn_statements_enabled() ? "enabled" : "disabled");
    BOOST_LOG_TRIVIAL(debug) << "Err on failure "
                             << (config.global().err_on_failure() ? "enabled" : "disabled");
    BOOST_LOG_TRIVIAL(info) << "Operating in mode " << config.global().mode();

    if (config.global().input_file_paths().empty()) {
      BOOST_LOG_TRIVIAL(info) << "Parsing stdin";
      return run_file(config, cin);
    }
    for (const auto &file : config.global().input_file_paths()) {
      BOOST_LOG_TRIVIAL(info) << "Parsing file " << file;
      ifstream input(file);
      int ret = run_file(config, input);
      if (ret != 0) {
        return ret;
      }
    }
  } catch (const std::runtime_error& e) {
    // Catch specific errors thrown by the ConfigOptions initialization.
    // If help was requested, just print the message (which includes help text).
    // Otherwise, it's a genuine application error.
    if (std::string(e.what()).starts_with("Help requested:")) {
      std::cout << e.what() << "\n";
      return 0; // Exit with success code after showing help
    }
    // For other runtime errors (parsing, file open, dependencies), print to cerr.
    std::cerr << "Application Error: " << e.what() << "\n";
    return 1; // Exit with error code
  }

  return 0; // Indicate successful execution
}
