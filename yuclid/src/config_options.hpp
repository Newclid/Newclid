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
#pragma once

#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/log/trivial.hpp>
#include <boost/program_options/options_description.hpp>
#include <iostream>
#include <string>
#include <vector>

namespace Yuclid {
  class Dist;
  class SquaredDist;

  /**
   * @brief Configuration options for Yuclid.
   *
   * The options are separated in two groups:
   *
   * - *global options* include mode of operation,
   *   input/output format, input files etc;
   * - *solver options* allow users to choose
   *   what AR tables are enabled etc.
   */
  class Config {
  public:
    /**
     * @brief Mode of operation for the application.
     *
     * Currently, only two modes are available:
     *
     * - run DD/AR on the problem(s);
     * - numerically match theorems and print the matches.
     */
    enum class Mode : uint8_t {
      DDAR,    //< Run DD/AR on a problem (default)
      MATCH,   //< Match all theorems and print them
    };

    /**
     * @brief Class to hold global configuration options.
     */
    class Global {
    public:
      [[nodiscard]] Mode mode() const { return m_mode; }

      [[nodiscard]] boost::log::trivial::severity_level log_level() const {
        return m_log_level;
      }

      [[nodiscard]] bool use_json() const { return m_use_json; }

      [[nodiscard]] const std::vector<std::string>& input_file_paths() const {
        return m_input_file_paths;
      }

      [[nodiscard]] bool err_on_failure() const { return m_err_on_failure; }

      /**
       * @brief An `options_description` object that can be used to initialize `this`.
       */
      [[nodiscard]] boost::program_options::options_description options_description();

    private:
      Mode m_mode = Mode::DDAR;
      boost::log::trivial::severity_level m_log_level = boost::log::trivial::info;
      bool m_use_json = false;
      std::vector<std::string> m_input_file_paths;
      bool m_err_on_failure = false;
    };

    /**
     * @brief Class to hold solver-specific feature flags.
     */
    class Solver {
    public:
      // Public accessors for solver options.
      template <typename VarT>
      [[nodiscard]] bool ar_enabled() const;

      [[nodiscard]] bool ar_sin_enabled() const {
        return !m_disable_ar_sin;
      }

      [[nodiscard]] bool eqn_statements_enabled() const {
        return !m_disable_eqn_statements;
      }

      /**
       * @brief An `options_description` object that can be used to initialize `this`.
       */
      [[nodiscard]] boost::program_options::options_description options_description();

    private:
      bool m_disable_ar_dist = false;
      bool m_disable_ar_squared = false;
      bool m_disable_ar_sin = true;
      bool m_disable_eqn_statements = false;
    };

    /**
     * @brief Build a `Config` object from the command line.
     */
    Config(int argc, char *argv[]); // NOLINT(*-avoid-c-arrays)

    [[nodiscard]] const Global &global() const { return m_global; }
    [[nodiscard]] const Solver &solver() const { return m_solver; }
  private:
    /** Global options. */
    Global m_global;
    /** Solver options. */
    Solver m_solver;
  };

  /**
   * @brief Operator to stream a Mode enum from an istream.
   */
  std::istream& operator>>(std::istream& input, Config::Mode& mode);

  /**
   * @brief Operator to stream a Mode enum to an ostream.
   */
  std::ostream &operator<<(std::ostream &out, const Config::Mode &mode);

  extern template bool Config::Solver::ar_enabled<Dist>() const;
  extern template bool Config::Solver::ar_enabled<SquaredDist>() const;
} // namespace Yuclid
