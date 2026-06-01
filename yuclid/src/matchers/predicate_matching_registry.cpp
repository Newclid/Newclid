#include "matchers/predicate_matching_registry.hpp"

#include <string>

namespace Yuclid {
namespace  {
    struct PredicateMatcherDefinition {
        std::string_view name;
        PredicateMatchingRole role;
        int base_cost;
    };

    constexpr PredicateMatcherDefinition PREDICATE_MATCHER_DEFINITIONS[] = {
        // Generator predicates.
        {"coll", PredicateMatchingRole::Generator, 10},
        {"cong", PredicateMatchingRole::Generator, 20},
        {"para", PredicateMatchingRole::Generator, 30},
        {"perp", PredicateMatchingRole::Generator, 30},

        // Simple filter predicates.
        {"diff", PredicateMatchingRole::Filter, 100},
        {"ncoll", PredicateMatchingRole::Filter, 100},
        {"npara", PredicateMatchingRole::Filter, 100},
        {"nperp", PredicateMatchingRole::Filter, 100},

        // More complex predicates kept as filters until optimized handling exists.
        {"eqangle", PredicateMatchingRole::Filter, 200},
        {"equal_angles", PredicateMatchingRole::Filter, 200},
        {"midp", PredicateMatchingRole::Filter, 200},
        {"cyclic", PredicateMatchingRole::Filter, 300},
        {"circle", PredicateMatchingRole::Filter, 300},
        {"circumcenter", PredicateMatchingRole::Filter, 300},
        {"eqratio", PredicateMatchingRole::Filter, 300},

        // Triangle predicates.
        {"simtri", PredicateMatchingRole::Filter, 400},
        {"simtrir", PredicateMatchingRole::Filter, 400},
        {"contri", PredicateMatchingRole::Filter, 400},
        {"contrir", PredicateMatchingRole::Filter, 400},

        // Constant predicates.
        {"rconst", PredicateMatchingRole::Filter, 200},
        {"r2const", PredicateMatchingRole::Filter, 200},
        {"lconst", PredicateMatchingRole::Filter, 200},
        {"l2const", PredicateMatchingRole::Filter, 200},
        {"aconst", PredicateMatchingRole::Filter, 200},

        // Other numerical/geometric filters.
        {"sameclock", PredicateMatchingRole::Filter, 300},
        {"obtuse_angle", PredicateMatchingRole::Filter, 200},
        {"sameside", PredicateMatchingRole::Filter, 300},
        {"nsameside", PredicateMatchingRole::Filter, 300},
    };

} // namespace
  
    PredicateMatchingStrategy::PredicateMatchingStrategy() :
        m_unsupported_strategy{PredicateMatchingRole::Unsupported, 1'000'000}
    {
        
    }

}
