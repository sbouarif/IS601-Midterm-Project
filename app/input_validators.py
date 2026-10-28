from app.exceptions import InvalidInputError


def validate_number(value):
    """Validate and convert a value to a float."""
    try:
        return float(value)
    except (ValueError, TypeError) as exc:
        raise InvalidInputError(f"Invalid number: {value}") from exc


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

    if operation.lower() not in valid_operations:
        raise InvalidInputError(f"Invalid operation: {operation}")

    return operation.lower()