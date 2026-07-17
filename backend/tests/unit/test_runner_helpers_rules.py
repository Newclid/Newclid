from typing import Any

import pytest
from newclid_backend import runner_helpers


def _custom_theorem(**overrides: Any) -> dict[str, Any]:
    theorem: dict[str, Any] = {
        "name": "custom_theorem",
        "description": "Example custom theorem",
        "premises": ["coll A B C", "perp A B C D"],
        "conclusions": ["para A B C D"],
    }
    theorem.update(overrides)
    return theorem


def test_as_str_tuple_converts_string_list_to_tuple() -> None:
    result = runner_helpers._as_str_tuple(["coll A B C", "perp A B C D"], "premises")
    assert result == ("coll A B C", "perp A B C D")


@pytest.mark.parametrize(
    "value", [None, "coll A B C", ("coll A B C",), {"predicate": "coll A B C"}]
)
def test_as_str_tuple_rejects_non_list_values(value: Any) -> None:
    with pytest.raises(ValueError, match="premises"):
        runner_helpers._as_str_tuple(value, "premises")


@pytest.mark.parametrize("value", [["coll A B C", 1], ["coll A B C", None], [False]])
def test_as_str_tuple_rejects_non_string_elements(value: list[Any]) -> None:
    with pytest.raises(ValueError, match="conclusions"):
        runner_helpers._as_str_tuple(value, "conclusions")


def test_build_custom_rule_fields_builds_expected_fields() -> None:
    result = runner_helpers._build_custom_rule_fields([_custom_theorem()])
    assert result == [
        {
            "id": "custom_theorem",
            "description": "Example custom theorem",
            "premises_txt": ("coll A B C", "perp A B C D"),
            "conclusions_txt": ("para A B C D",),
        }
    ]


def test_build_custom_rule_fields_preserves_input_order() -> None:
    result = runner_helpers._build_custom_rule_fields(
        [
            _custom_theorem(name="first_theorem"),
            _custom_theorem(name="second_theorem"),
            _custom_theorem(name="third_theorem"),
        ]
    )
    assert [fields["id"] for fields in result] == [
        "first_theorem",
        "second_theorem",
        "third_theorem",
    ]


@pytest.mark.parametrize("description", [None, ""])
def test_build_custom_rule_fields_defaults_empty_description_to_name(
    description: Any,
) -> None:
    result = runner_helpers._build_custom_rule_fields(
        [_custom_theorem(description=description)]
    )
    assert result[0]["description"] == "custom_theorem"


def test_build_custom_rule_fields_defaults_missing_description_to_name() -> None:
    theorem = _custom_theorem()
    del theorem["description"]
    result = runner_helpers._build_custom_rule_fields([theorem])
    assert result[0]["description"] == "custom_theorem"


def test_build_custom_rule_fields_rejects_missing_name() -> None:
    theorem = _custom_theorem()
    del theorem["name"]
    with pytest.raises(
        ValueError, match="Custom theorem field 'name' must be a string"
    ):
        runner_helpers._build_custom_rule_fields([theorem])


@pytest.mark.parametrize("name", [None, 123, ["custom_theorem"]])
def test_build_custom_rule_fields_rejects_non_string_name(name: Any) -> None:
    with pytest.raises(
        ValueError, match="Custom theorem field 'name' must be a string"
    ):
        runner_helpers._build_custom_rule_fields([_custom_theorem(name=name)])


@pytest.mark.parametrize("description", [123, ["Description"], {"text": "Description"}])
def test_build_custom_rule_fields_rejects_non_string_description(
    description: Any,
) -> None:
    with pytest.raises(
        ValueError, match="Custom theorem field 'description' must be a string"
    ):
        runner_helpers._build_custom_rule_fields(
            [_custom_theorem(description=description)]
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("premises", "coll A B C"),
        ("premises", ["coll A B C", 123]),
        ("premises", None),
        ("conclusions", "para A B C D"),
        ("conclusions", ["para A B C D", None]),
        ("conclusions", None),
    ],
)
def test_build_custom_rule_fields_rejects_invalid_predicate_lists(
    field_name: str, invalid_value: Any
) -> None:
    theorem = _custom_theorem()
    theorem[field_name] = invalid_value
    with pytest.raises(ValueError, match=field_name):
        runner_helpers._build_custom_rule_fields([theorem])
