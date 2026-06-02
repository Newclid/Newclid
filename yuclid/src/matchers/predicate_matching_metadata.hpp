#pragma once

#include <string_view>

namespace Yuclid {

/**
 * Describes the intended role of a predicate in the optimized generic matcher.
 *
 * This metadata is only a planning hint. It does not mean that a concrete
 * provider/checker for the predicate has already been implemented.
 *
 * If a predicate has no implemented provider yet, the optimized matcher should
 * still remain correct by enumerating the remaining unmapped variables and then
 * relying on the existing theorem-building and final numerical checks.
 */
enum class PredicateMatchingRole {
    /**
     * The predicate can generate candidate mappings when a matching provider
     * and geometry index/cache exist.
     *
     * Example predicates:
     *   coll, cong, para, perp
     *
     * Example:
     *   coll A B C
     *
     * A future coll provider can use the collinearity index to generate
     * possible assignments for A, B, and C, or to extend an existing partial
     * mapping if some of these variables are already assigned.
     *
     * Being classified as CandidateGenerator does not mean that the provider
     * already exists. If the provider is missing, matching falls back to
     * enumerating the remaining variables.
     */ 
    CandidateGenerator,

    /**
     * The predicate does not generate candidates, but can reject a matching
     * state once all variables used by the predicate are assigned.
     *
     * Note: this example is here to demonstrate how in future it might work
     * Currently no parser supports those predicates and Yuclid also doesn't support
     * them anywhere so for now such example is not possible
     *
     * Example predicates:
     *   diff, ncoll, npara, nperp
     *
     * Example:
     *   ncoll A B C
     *
     * If only A and B are assigned, the predicate cannot be checked yet.
     * Once A, B, and C are assigned, the matcher can reject the state if the
     * mapped points are collinear.
     *
     * If no checker is implemented yet, correctness is still preserved by
     * final theorem validation.
     */
    CandidateFilter,

     /**
     * The predicate is not used during optimized search for now.
     *
     * These predicates are handled only after a complete mapping has been
     * produced, through the existing theorem-building and final numerical
     * validation path.
     *
     * Example predicates:
     *   eqangle, midp, cyclic, simtri, eqratio, rconst
     *
     * This role is useful for predicates that are supported by StatementBuilder
     * and final checks, but do not yet have specialized matching providers.
     */
    Validator,

    /**
     * The optimized matcher should not handle this predicate directly.
     *
     * Unknown predicates should not be silently ignored. Later matching logic
     * should either fall back to the naive matcher for the whole rule or report
     * a clear unsupported-predicate error.
     */
    Unsupported,
};

struct PredicateMatchingMetadata {
    PredicateMatchingRole role;

    /**
     * Rough static cost hint used for planning/order decisions.
     *
     * This value is only a heuristic. It must never affect correctness.
     * Later predicate providers may provide more precise dynamic estimates
     * based on the current partial mapping.
     */
    int base_cost;
};

[[nodiscard]] PredicateMatchingMetadata predicate_matching_metadata(
    std::string_view predicate_name
);

[[nodiscard]] PredicateMatchingRole predicate_matching_role(
    std::string_view predicate_name
);

[[nodiscard]] int predicate_matching_base_cost(
    std::string_view predicate_name
);

[[nodiscard]] std::string_view predicate_matching_role_name(
    PredicateMatchingRole role
);

[[nodiscard]] bool is_candidate_generator(
    std::string_view predicate_name
);

[[nodiscard]] bool is_candidate_filter(
    std::string_view predicate_name
);

[[nodiscard]] bool is_final_validator(
    std::string_view predicate_name
);

[[nodiscard]] bool is_unsupported_predicate(
    std::string_view predicate_name
);


}
