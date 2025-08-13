import itertools

from newclid.rule_matching.permutations import generate_permutations_as_dicts


def test_output_is_correct():
    variables = ["a"]
    points = ["x", "y", "z", "w"]

    baseline_list = [
        {v: p for v, p in zip(variables, point_list)}
        for point_list in itertools.permutations(points, r=len(variables))
    ]

    permutation_generator_list = list(generate_permutations_as_dicts(points, variables))

    print(len(baseline_list))
    print(baseline_list[:3])
    print(permutation_generator_list[:3])

    assert len(baseline_list) == len(permutation_generator_list)

    baseline = set(tuple(sorted(mapping.items())) for mapping in baseline_list)
    permutation_generator_set = set(
        tuple(sorted(mapping.items())) for mapping in permutation_generator_list
    )

    assert baseline == permutation_generator_set
