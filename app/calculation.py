from datetime import datetime

from app.operations import OperationFactory


class Calculation:
    """Represents a calculation with its result and timestamp."""

    def __init__(self, operation, a, b, timestamp=None, result=None):
        self.operation = operation
        self.a = a
        self.b = b
        self.timestamp = (
            datetime.now() if timestamp is None else timestamp
        )
        self.result = result

    def perform(self):
        """Perform the calculation and store its result."""
        operation = OperationFactory.create_operation(self.operation)
        self.result = operation.execute(self.a, self.b)
        return self.result

    def to_dict(self):
        """Convert the calculation to a serializable dictionary."""
        if self.result is None:
            self.perform()

        return {
            "operation": self.operation,
            "a": self.a,
            "b": self.b,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self):
        """Return a readable representation of the calculation."""
        if self.result is None:
            self.perform()

        return f"{self.operation} {self.a} {self.b} = {self.result}"