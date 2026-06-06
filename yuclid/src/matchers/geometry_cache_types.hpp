#pragma once

#include <cstddef>
#include <vector>

#include "matchers/matching_types.hpp"

namespace Yuclid {
    struct Segment {
        ProblemPointIndex first;
        ProblemPointIndex second;
    };

    using SegmentId = std::size_t;

    struct SegmentBuckets {
        std::vector<std::vector<SegmentId>> buckets;
    };
}
