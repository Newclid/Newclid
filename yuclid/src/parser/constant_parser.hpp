#pragma once

#include "typedef.hpp"

#include <cctype>
#include <format>
#include <sstream>
#include <string>
#include <system_error>
#include <type_traits>

namespace Yuclid {

    [[noreturn]] inline void throw_invalid_rational_constant(
            const std::string& value
            ) {
        throw std::system_error(
                std::make_error_code(std::errc::invalid_argument),
                std::format("Invalid rational constant '{}'", value)
                );
    }

    /**
     * Shared legacy constant parser used by both ProblemParser and StatementBuilder.
     *
     * StatementBuilder intentionally mirrors ProblemParser when converting custom
     * rule predicates such as rconst, r2const, lconst, l2const, and aconst into
     * Yuclid statements.
     *
     * The old parser relied directly on boost::rational stream extraction. That
     * made malformed constants platform-dependent: GCC/libstdc++ and MSVC do not
     * always report malformed input in the same way.
     *
     * This helper keeps the legacy extraction semantics for accepted tokens, but
     * rejects obviously malformed fraction syntax before stream extraction so both
     * parsers behave consistently on all platforms.
     *
     * Kept as legacy:
     *   5      -> stream extraction decides/defaults
     *   12/0   -> stream extraction decides/defaults
     *
     * Rejected before extraction:
     *   5/
     *   /5
     *   5/abc
     *   a/5
     *   5/2x
     *   1/2/3
     */
    inline void validate_legacy_rational_constant_token(
            const std::string& value
            ) {
        if (value.empty()) {
            throw_invalid_rational_constant(value);
        }

        const std::size_t slash_pos = value.find('/');

        if (
                slash_pos != std::string::npos &&
                value.find('/', slash_pos + 1) != std::string::npos
           ) {
            throw_invalid_rational_constant(value);
        }

        const std::size_t numerator_end =
            slash_pos == std::string::npos ? value.size() : slash_pos;

        std::size_t numerator_start = 0;

        if (value[numerator_start] == '+' || value[numerator_start] == '-') {
            ++numerator_start;
        }

        if (numerator_start == numerator_end) {
            throw_invalid_rational_constant(value);
        }

        for (std::size_t i = numerator_start; i < numerator_end; ++i) {
            if (!std::isdigit(static_cast<unsigned char>(value[i]))) {
                throw_invalid_rational_constant(value);
            }
        }

        if (slash_pos == std::string::npos) {
            return;
        }

        const std::size_t denominator_start = slash_pos + 1;

        if (denominator_start == value.size()) {
            throw_invalid_rational_constant(value);
        }

        for (std::size_t i = denominator_start; i < value.size(); ++i) {
            if (!std::isdigit(static_cast<unsigned char>(value[i]))) {
                throw_invalid_rational_constant(value);
            }
        }
    }

    template <typename ExpectedConstType>
        ExpectedConstType parse_legacy_rational_constant(
                const std::string& value
                ) {
            static_assert(
                    std::is_same_v<ExpectedConstType, NNRat> ||
                    std::is_same_v<ExpectedConstType, Rat>,
                    "parse_legacy_rational_constant can only be used with NNRat or Rat"
                    );

            validate_legacy_rational_constant_token(value);

            std::istringstream value_stream(value);

            ExpectedConstType result;
            value_stream >> result;

            // Important: do not check failbit here.
            //
            // This preserves the existing Yuclid/JGEX compatibility behaviour where
            // some failed rational extractions intentionally return the default value.
            return result;
        }

    template <typename ExpectedConstType>
        ExpectedConstType parse_legacy_rational_constant_from_stream(
                std::istringstream& input
                ) {
            std::string value;

            if (!(input >> value)) {
                throw_invalid_rational_constant(value);
            }

            return parse_legacy_rational_constant<ExpectedConstType>(value);
        }

}
