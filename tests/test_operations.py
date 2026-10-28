import pytest
from app.operations import (
    OperationFactory,
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
    PowerOperation,
    RootOperation,
)


@pytest.mark.parametrize(
    "operation_class,a,b,expected",
    [
        (AddOperation, 5, 3, 8),
        (SubtractOperation, 5, 3, 2),
        (MultiplyOperation, 5, 3, 15),
        (DivideOperation, 6, 3, 2),
        (PowerOperation, 2, 3, 8),
        (RootOperation, 9, 2, 3),
    ],
)
def test_operations(operation_class, a, b, expected):
    operation = operation_class()
    assert operation.execute(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    "name,expected_class",
    [
        ("add", AddOperation),
        ("subtract", SubtractOperation),
        ("multiply", MultiplyOperation),
        ("divide", DivideOperation),
        ("power", PowerOperation),
        ("root", RootOperation),
    ],
)
def test_operation_factory(name, expected_class):
    operation = OperationFactory.create_operation(name)
    assert isinstance(operation, expected_class)


def test_factory_is_case_insensitive():
    assert isinstance(OperationFactory.create_operation("ADD"), AddOperation)


def test_invalid_operation():
    with pytest.raises(ValueError, match="Unknown operation"):
        OperationFactory.create_operation("invalid")


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        DivideOperation().execute(10, 0)


def test_zero_degree_root():
    with pytest.raises(ValueError, match="Root degree cannot be zero"):
        RootOperation().execute(9, 0)


def test_even_root_negative_number():
    with pytest.raises(ValueError, match="even root"):
        RootOperation().execute(-16, 2)


def test_odd_root_negative_number():
    assert RootOperation().execute(-8, 3) == pytest.approx(-2)


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("modulus", 10, 3, 1),
        ("int_divide", 10, 3, 3),
        ("percent", 25, 200, 12.5),
        ("abs_diff", 5, 12, 7),
        ("abs_diff", 12, 5, 7),
        ("modulus", 10, 5, 0),
    ],
)
def test_new_operations(operation, a, b, expected):
    operation_obj = OperationFactory.create_operation(operation)
    assert operation_obj.execute(a, b) == expected


@pytest.mark.parametrize(
    "operation",
    ["modulus", "int_divide", "percent"],
)
def test_new_operations_zero_division(operation):
    operation_obj = OperationFactory.create_operation(operation)

    with pytest.raises(ZeroDivisionError):
        operation_obj.execute(10, 0)