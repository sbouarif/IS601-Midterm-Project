# IS601 Midterm Project – Enhanced Python Calculator

This project is an enhanced command-line calculator developed for the IS601 Midterm Project at NJIT, building upon the Module 5 Advanced Python Calculator. It demonstrates object-oriented programming, design patterns, pandas-based data management, automated testing, error handling, logging, and continuous integration.

The midterm enhancements include four additional arithmetic operations, improved input validation, comprehensive logging of successful and failed calculations, expanded automated testing, and color-coded terminal outputs for improved usability.

## Features

- Interactive command-line calculator (REPL)
- Ten supported arithmetic operations:
  - Addition (`add`)
  - Subtraction (`subtract`)
  - Multiplication (`multiply`)
  - Division (`divide`)
  - Exponentiation (`power`)
  - Root calculation (`root`)
  - Modulus (`modulus`)
  - Integer division (`int_divide`)
  - Percentage calculation (`percent`)
  - Absolute difference (`abs_diff`)
- Calculation history management using pandas DataFrames
- Save and load calculation history using CSV files
- Automatic history saving through the Observer Design Pattern
- Undo and redo functionality using the Memento Design Pattern
- Environment-based configuration management
- Input validation for numeric values and supported operations
- Robust error handling for invalid inputs and calculation failures
- Comprehensive logging of successful calculations and errors
- Color-coded terminal outputs using Colorama for improved readability
- Object-oriented programming with reusable calculator components
- Factory Design Pattern for creating arithmetic operations
- Automated unit testing with pytest
- 100% test coverage verified during development
- GitHub Actions continuous integration for automated testing

## Design Patterns

The application demonstrates several design patterns:

- **Factory Pattern** - Creates operation objects based on user input.
- **Strategy Pattern** - Provides interchangeable arithmetic operation classes.
- **Observer Pattern** - Monitors history changes and supports automatic saving.
- **Memento Pattern** - Stores and restores history states for undo and redo.
- **Facade Pattern** - The Calculator class provides a simplified interface to the application's components.

## Project Structure

```text
app/
├── calculator_repl.py
├── calculation.py
├── calculator_config.py
├── calculator_memento.py
├── exceptions.py
├── history.py
├── input_validators.py
└── operations.py

tests/
├── test_calculations.py
├── test_calculator_repl.py
├── test_calculator_config.py
├── test_calculator_memento.py
├── test_exceptions.py
├── test_history.py
├── test_input_validators.py
└── test_operations.py



## Midterm Project Enhancements

### New Calculator Operations

| Operation | Command | Example | Result |
|---|---|---|---|
| Modulus | `modulus` | `modulus 10 3` | 1 |
| Integer Division | `int_divide` | `int_divide 10 3` | 3 |
| Percentage | `percent` | `percent 25 200` | 12.5 |
| Absolute Difference | `abs_diff` | `abs_diff 5 12` | 7 |

### Logging and Error Handling

The calculator uses Python's built-in `logging` module to record successful calculations and errors. Successful operations are logged at the INFO level, while calculation failures are logged with exception details.

Input validation prevents unsupported operations and invalid numeric inputs. Division-related operations also handle division by zero.

### Color-Coded Terminal Output

The application uses Colorama to improve the readability of terminal output. Color-coded messages help users distinguish successful calculations, errors, and informational feedback.

### Running the Calculator

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the calculator:

```bash
python main.py
```

Enter `help` to view commands, or enter an operation followed by two numbers.

Example:

```text
modulus 10 3
```

### Automated Testing

Run the complete test suite:

```bash
python -m pytest
```

The test suite includes tests for the calculator's operations, input validation, history management, and other application features.