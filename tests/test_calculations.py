import pytest
from app.calculation import Calculation


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", 10, 5, 15),
        ("subtract", 10, 5, 5),
        ("multiply", 10, 5, 50),
        ("divide", 10, 5, 2),
        ("power", 2, 3, 8),
        ("root", 16, 2, 4),
    ],
)
def test_calculation_perform(operation, a, b, expected):
    calculation = Calculation(operation, a, b)
    assert calculation.perform() == pytest.approx(expected)


def test_calculation_to_dict():
    calculation = Calculation("add", 5, 3)

    assert calculation.to_dict() == {
        "operation": "add",
        "a": 5,
        "b": 3,
        "result": 8,
    }


def test_calculation_string():
    calculation = Calculation("multiply", 4, 5)
    assert str(calculation) == "multiply 4 5 = 20"