import pytest
from app.exceptions import (
    CalculatorError,
    InvalidInputError,
    InvalidOperationError,
    ConfigurationError,
    HistoryError,
)


@pytest.mark.parametrize(
    "exception_class",
    [
        InvalidInputError,
        InvalidOperationError,
        ConfigurationError,
        HistoryError,
    ],
)
def test_exceptions_inherit_from_calculator_error(exception_class):
    assert issubclass(exception_class, CalculatorError)


@pytest.mark.parametrize(
    "exception_class,message",
    [
        (CalculatorError, "Calculator error"),
        (InvalidInputError, "Invalid input"),
        (InvalidOperationError, "Invalid operation"),
        (ConfigurationError, "Configuration error"),
        (HistoryError, "History error"),
    ],
)
def test_exception_messages(exception_class, message):
    with pytest.raises(exception_class, match=message):
        raise exception_class(message)