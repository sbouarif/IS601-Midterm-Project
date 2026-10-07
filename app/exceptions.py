class CalculatorError(Exception):
    """Base exception for calculator errors."""
    pass


class InvalidInputError(CalculatorError):
    """Raised when user input is invalid."""
    pass


class InvalidOperationError(CalculatorError):
    """Raised when an unsupported operation is requested."""
    pass


class ConfigurationError(CalculatorError):
    """Raised when calculator configuration is invalid."""
    pass


class HistoryError(CalculatorError):
    """Raised when an error occurs with calculation history."""
    pass