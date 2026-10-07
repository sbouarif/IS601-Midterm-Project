# Module 5 - Advanced Python Calculator

This project is a command-line calculator developed for IS601 Module 5. It demonstrates advanced object-oriented programming, design patterns, pandas data management, configuration management, error handling, automated testing, and continuous integration.

## Features

- Interactive REPL calculator
- Addition, subtraction, multiplication, division, power, and root operations
- Calculation history using pandas DataFrames
- Save and load history using CSV files
- Automatic history saving
- Undo and redo functionality
- Environment-based configuration
- Input validation and error handling
- 100% automated test coverage

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