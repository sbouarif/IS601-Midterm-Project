import math

from app.exceptions import InvalidInputError


def validate_number(value):
    """Validate and convert a finite numeric value to a float."""
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise InvalidInputError(f"Invalid number: {value}") from exc

    if not math.isfinite(number):
        raise InvalidInputError(
            "Number must be finite (not NaN or infinity)."
        )

    return number


def validate_operation(operation):
    """Validate that an operation is supported."""
    valid_operations = {
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "root",
        "modulus",
        "int_divide",
        "percent",
        "abs_diff",
    }

    if not isinstance(operation, str):
        raise InvalidInputError("Operation must be a string.")

    operation = operation.lower()

    if operation not in valid_operations:
        raise InvalidInputError(f"Invalid operation: {operation}")

    return operation