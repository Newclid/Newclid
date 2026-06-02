#include "matchers/predicate_matching_metadata.hpp"

namespace Yuclid {

namespace {
struct PredicateMetadataDefinition {
    std::string_view name;
    PredicateMatchingRole role;
    int base_cost;
};

constexpr int UNSUPPORTED_PREDICATE_COST = 1'000'000;

constexpr PredicateMetadataDefinition PREDICATE_METADATA_DEFINITIONS[] = {
    // Candidate generators.
    // These predicates can generate candidate mappings from geometry indexes.
    {"coll", PredicateMatchingRole::CandidateGenerator, 10},
    {"cong", PredicateMatchingRole::CandidateGenerator, 20},
    {"para", PredicateMatchingRole::CandidateGenerator, 30},
    {"perp", PredicateMatchingRole::CandidateGenerator, 30},

    // Validators.
    // These predicates are used in the final step of theorem validation,
    // but are not used during optimized search yet.
    {"eqangle", PredicateMatchingRole::Validator, 200},
    {"equal_angles", PredicateMatchingRole::Validator, 200},

    {"midp", PredicateMatchingRole::Validator, 150},

    {"cyclic", PredicateMatchingRole::Validator, 250},
    {"circle", PredicateMatchingRole::Validator, 250},
    {"circumcenter", PredicateMatchingRole::Validator, 250},

    {"eqratio", PredicateMatchingRole::Validator, 250},

    {"simtri", PredicateMatchingRole::Validator, 300},
    {"simtrir", PredicateMatchingRole::Validator, 300},
    {"contri", PredicateMatchingRole::Validator, 300},
    {"contrir", PredicateMatchingRole::Validator, 300},

    {"rconst", PredicateMatchingRole::Validator, 150},
    {"r2const", PredicateMatchingRole::Validator, 150},
    {"lconst", PredicateMatchingRole::Validator, 150},
    {"l2const", PredicateMatchingRole::Validator, 150},
    {"aconst", PredicateMatchingRole::Validator, 150},

    {"sameclock", PredicateMatchingRole::Validator, 200},
    {"obtuse_angle", PredicateMatchingRole::Validator, 200},
    {"sameside", PredicateMatchingRole::Validator, 200},
    {"nsameside", PredicateMatchingRole::Validator, 200},
};

}

PredicateMatchingMetadata predicate_matching_metadata(
    std::string_view predicate_name
) {
    for (const auto &definition : PREDICATE_METADATA_DEFINITIONS) {
        if (definition.name == predicate_name) {
            return {
                definition.role,
                definition.base_cost,
            };
        }
    }

    return {
        PredicateMatchingRole::Unsupported,
        UNSUPPORTED_PREDICATE_COST,
    };
}

PredicateMatchingRole predicate_matching_role(
    std::string_view predicate_name
) {
    return predicate_matching_metadata(predicate_name).role;
}

int predicate_matching_base_cost(
    std::string_view predicate_name
) {
    return predicate_matching_metadata(predicate_name).base_cost;
}

std::string_view predicate_matching_role_name(
    PredicateMatchingRole role
) {
    switch (role) {
        case PredicateMatchingRole::CandidateGenerator:
            return "CandidateGenerator";
        case PredicateMatchingRole::CandidateFilter:
            return "CandidateFilter";
        case PredicateMatchingRole::Validator:
            return "FinalValidator";
        case PredicateMatchingRole::Unsupported:
            return "Unsupported";
    }

    return "Unsupported";
}

bool is_candidate_generator(
    std::string_view predicate_name
) {
    return predicate_matching_role(predicate_name)
        == PredicateMatchingRole::CandidateGenerator;
}

bool is_candidate_filter(
    std::string_view predicate_name
) {
    return predicate_matching_role(predicate_name)
        == PredicateMatchingRole::CandidateFilter;
}

bool is_final_validator(
    std::string_view predicate_name
) {
    return predicate_matching_role(predicate_name)
        == PredicateMatchingRole::Validator;
}

bool is_unsupported_predicate(
    std::string_view predicate_name
) {
    return predicate_matching_role(predicate_name)
        == PredicateMatchingRole::Unsupported;
}

}
