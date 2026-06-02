#pragma once

#include <string_view>

namespace Yuclid {

enum class PredicateMatchingRole {
    CandidateGenerator,
    CandidateFilter,
    Validator,
    Unsupported,
};

struct PredicateMatchingMetadata {
    PredicateMatchingRole role;
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
