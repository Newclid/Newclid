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
#include "config_options.hpp"

#include "type/dist.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"

#include <boost/log/trivial.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/program_options.hpp> // NOLINT
#include <boost/program_options/options_description.hpp>
#include <iostream>
#include <istream>
#include <ostream>
#include <string>

namespace po = boost::program_options;

namespace Yuclid {

  /**
   * @brief Operator to stream a Mode enum from an istream.
   */
  std::istream& operator>>(std::istream& input, Config::Mode& mode) {
    std::string str;
    input >> str;
    if (str == "ddar") {
      mode = Config::Mode::DDAR;
    } else if (str == "match") {
      mode = Config::Mode::MATCH;
    } else {
      throw po::validation_error(po::validation_error::invalid_option_value, "mode", str);
    }
    return input;
  }

  std::ostream &operator<<(std::ostream &out, const Config::Mode &mode) {
    switch (mode) {
    case Config::Mode::DDAR:
      return out << "ddar";
    case Config::Mode::MATCH:
      return out << "match";
    }
    return out;
  }

  template <typename VarT>
  bool Config::Solver::ar_enabled() const {
    if constexpr (std::is_same_v<VarT, Dist>) {
      return !m_disable_ar_dist;
    } else if constexpr (std::is_same_v<VarT, SquaredDist>) {
      return !m_disable_ar_squared;
    } else if constexpr (std::is_same_v<VarT, SinOrDist>) {
      return !m_disable_ar_sin;
    } else if constexpr (std::is_same_v<VarT, SlopeAngle>) {
      return true; // SlopeAngle is always enabled
    } else {
      static_assert(false, "Type is unsupported");
    }
  }

  template bool Config::Solver::ar_enabled<Dist>() const;
  template bool Config::Solver::ar_enabled<SquaredDist>() const;

  po::options_description Config::Global::options_description() {
    po::options_description desc("Program options");
    desc.add_options()
      ("help", "produce help message")
      ("err-on-failure", po::bool_switch(&m_err_on_failure),
       "Exit with nonzero return code if failed to solve the problem (default: no)")
      ("use-json", po::bool_switch(&m_use_json),
       "Use json for output. Currently, only used in `--mode=match`")
      ("input-file", po::value<std::vector<std::string>>(&m_input_file_paths)->multitoken(),
       "Input file paths. If not specified, standard input (std::cin) is used.")
      ("log-level", po::value<boost::log::trivial::severity_level>(&m_log_level)->default_value(boost::log::trivial::info),
       "Set the minimum logging severity level (trace, debug, info, warning, error, fatal). Default: info.")
      ("mode", po::value<Mode>(&m_mode)->implicit_value(Mode::DDAR),
       "Operation mode. One of `ddar`, `datagen`, `match`. Default: `ddar`.");
    return desc;
  }

  po::options_description Config::Solver::options_description() {
    po::options_description desc("Program options");
    desc.add_options()
      ("disable-ar-dist", po::bool_switch(&m_disable_ar_dist),
       "Disable AR table for length chasing")
      ("disable-ar-squared", po::bool_switch(&m_disable_ar_squared),
       "Enable AR table for squared length chasing")
      ("disable-eqn-statements", po::bool_switch(&m_disable_eqn_statements),
       "Disable theorems with equations as hypotheses/conclusions (default: enabled)")
      ("disable-ar-sin", po::bool_switch(&m_disable_ar_sin),
       "Disable use of sines (recommended for now)");
    return desc;
  }

  Config::Config(int argc, char* argv[]) {

    // Define the command-line options using Boost.Program_options.
    po::options_description desc("Allowed options");
    desc.add(m_global.options_description()).add(m_solver.options_description());

    po::positional_options_description positional;
    positional.add("input-file", -1);

    po::variables_map vars;
    try {
      po::store(po::command_line_parser(argc, argv).
                options(desc).positional(positional).run(), vars);
      po::notify(vars);
    } catch (const po::error& e) {
      std::stringstream desc_str;
      desc_str << desc;
      throw std::runtime_error(std::string("Error parsing command line: ") + e.what() + "\n" + desc_str.str());
    }

#ifdef HAVE_VARIABLES_MAP_CONTAINS
    if (vars.contains("help")) {
#else
    if (vars.find("help") != vars.end()) { // NOLINT(readability-container-contains)
#endif
      std::stringstream desc_str;
      desc_str << desc;
      throw std::runtime_error(std::string("Help requested:\n") + desc_str.str());
    }
  }

} // namespace Yuclid
