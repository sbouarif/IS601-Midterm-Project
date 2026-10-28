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
class ModulusOperation(Operation):
    """Returns the remainder after division."""

    def execute(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot calculate modulus by zero.")
        return a % b


class IntegerDivideOperation(Operation):
    """Returns the integer quotient using floor division."""

    def execute(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a // b


class PercentOperation(Operation):
    """Calculates a as a percentage of b."""

    def execute(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot calculate percentage with a zero denominator.")
        return (a / b) * 100


class AbsoluteDifferenceOperation(Operation):
    """Returns the absolute difference between two numbers."""

    def execute(self, a, b):
        return abs(a - b)

class OperationFactory:
    """Factory for creating calculator operation objects."""

    operations = {
        "add": AddOperation,
        "subtract": SubtractOperation,
        "multiply": MultiplyOperation,
        "divide": DivideOperation,
        "power": PowerOperation,
        "root": RootOperation,
        "modulus": ModulusOperation,
        "int_divide": IntegerDivideOperation,
        "percent": PercentOperation,
        "abs_diff": AbsoluteDifferenceOperation,
    }

    @classmethod
    def create_operation(cls, operation_name):
        """Create an operation based on its name."""
        operation_class = cls.operations.get(operation_name.lower())

        if operation_class is None:
            raise ValueError(f"Unknown operation: {operation_name}")

        return operation_class()