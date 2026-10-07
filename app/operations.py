from abc import ABC, abstractmethod


class Operation(ABC):
    """Abstract base class for calculator operations."""

    @abstractmethod
    def execute(self, a, b):
        """Perform the operation."""
        pass  # pragma: no cover


class AddOperation(Operation):
    """Performs addition."""

    def execute(self, a, b):
        return a + b


class SubtractOperation(Operation):
    """Performs subtraction."""

    def execute(self, a, b):
        return a - b


class MultiplyOperation(Operation):
    """Performs multiplication."""

    def execute(self, a, b):
        return a * b


class DivideOperation(Operation):
    """Performs division."""

    def execute(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b


class PowerOperation(Operation):
    """Raises a number to a power."""

    def execute(self, a, b):
        return a ** b


class RootOperation(Operation):
    """Calculates the nth root of a number."""

    def execute(self, a, b):
        if b == 0:
            raise ValueError("Root degree cannot be zero.")
        if a < 0 and b % 2 == 0:
            raise ValueError("Cannot calculate an even root of a negative number.")
        if a < 0:
            return -((-a) ** (1 / b))
        return a ** (1 / b)


class OperationFactory:
    """Factory for creating calculator operation objects."""

    operations = {
        "add": AddOperation,
        "subtract": SubtractOperation,
        "multiply": MultiplyOperation,
        "divide": DivideOperation,
        "power": PowerOperation,
        "root": RootOperation,
    }

    @classmethod
    def create_operation(cls, operation_name):
        """Create an operation based on its name."""
        operation_class = cls.operations.get(operation_name.lower())

        if operation_class is None:
            raise ValueError(f"Unknown operation: {operation_name}")

        return operation_class()