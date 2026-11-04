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

    data = calculation.to_dict()

    assert data["operation"] == "add"
    assert data["a"] == 5
    assert data["b"] == 3
    assert data["result"] == 8
    assert data["timestamp"] == calculation.timestamp.isoformat()


def test_calculation_string():
    calculation = Calculation("multiply", 4, 5)
    assert str(calculation) == "multiply 4 5 = 20"