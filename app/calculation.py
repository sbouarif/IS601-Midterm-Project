from app.operations import OperationFactory


class Calculation:
    """Represents a single calculator calculation."""

    def __init__(self, operation, a, b):
        self.operation = operation
        self.a = a
        self.b = b

    def perform(self):
        """Perform the calculation using the selected operation."""
        operation = OperationFactory.create_operation(self.operation)
        return operation.execute(self.a, self.b)

    def to_dict(self):
        """Convert the calculation into a dictionary for history storage."""
        return {
            "operation": self.operation,
            "a": self.a,
            "b": self.b,
            "result": self.perform(),
        }

    def __str__(self):
        """Return a readable representation of the calculation."""
        result = self.perform()
        return f"{self.operation} {self.a} {self.b} = {result}"