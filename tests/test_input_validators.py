import pytest
from app.exceptions import InvalidInputError
from app.input_validators import validate_number, validate_operation


@pytest.mark.parametrize(
    "value,expected",
    [
        ("10", 10.0),
        ("3.5", 3.5),
        ("-7", -7.0),
        (5, 5.0),
    ],
)
def test_validate_number(value, expected):
    assert validate_number(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "",
        None,
    ],
)
def test_validate_number_invalid(value):
    with pytest.raises(InvalidInputError, match="Invalid number"):
        validate_number(value)


@pytest.mark.parametrize(
    "operation",
    [
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "root",
    ],
)
def test_validate_operation(operation):
    assert validate_operation(operation) == operation


def test_validate_operation_case_insensitive():
    assert validate_operation("ADD") == "add"


@pytest.mark.parametrize(
    "operation",
    [
        "invalid",
        "modulus",
        "hello",
    ],
)
def test_validate_operation_invalid(operation):
    with pytest.raises(InvalidInputError, match="Invalid operation"):
        validate_operation(operation)