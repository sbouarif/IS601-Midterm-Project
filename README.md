# IS601 Midterm Project – Enhanced Python Calculator

An enhanced command-line calculator developed for the IS601 Midterm Project at the New Jersey Institute of Technology (NJIT). The application extends the Module 5 Advanced Python Calculator and demonstrates object-oriented programming, design patterns, persistent calculation history, environment-based configuration, file logging, automated testing, and continuous integration.

## Features

- Interactive command-line calculator (REPL) with ten arithmetic operations
- Factory and Strategy patterns for arithmetic operations
- Pandas-based calculation history with timestamps
- CSV saving, loading, and optional automatic saving
- Undo and redo using the Memento pattern
- Observer-based automatic saving and history logging
- Configuration using `python-dotenv`, including input limits and precision
- Input validation and recoverable errors in the REPL
- Color-coded terminal output using Colorama
- Automated tests using pytest and GitHub Actions

## Project structure

```text
IS601-Midterm-Project/
├── .github/
│   └── workflows/
├── app/
│   ├── calculation.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── calculator_repl.py
│   ├── exceptions.py
│   ├── history.py
│   ├── input_validators.py
│   ├── logger.py
│   └── operations.py
├── tests/
│   ├── test_calculations.py
│   ├── test_calculator_config.py
│   ├── test_calculator_memento.py
│   ├── test_calculator_repl.py
│   ├── test_exceptions.py
│   ├── test_history.py
│   ├── test_input_validators.py
│   └── test_operations.py
├── .env.example
├── .gitignore
├── main.py
├── pytest.ini
├── README.md
└── requirements.txt
```

Generated logs, local history files, virtual environments, and coverage artifacts are excluded from version control by `.gitignore`.

## Installation and setup

**1. Clone the repository and switch to the revision branch:**

```bash
git clone https://github.com/sbouarif/IS601-Midterm-Project.git
cd IS601-Midterm-Project
git checkout midterm-revision
```

**2. Create and activate a virtual environment:**

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (Command Prompt):

```bat
python -m venv venv
venv\Scripts\activate.bat
```

**3. Install dependencies:**

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**4. Optionally create a local configuration file:**

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` using File Explorer or `copy .env.example .env` in Command Prompt. The calculator also uses default values if `.env` is absent.

**5. Start the calculator:**

```bash
python main.py
```

Enter `help` for instructions or `exit` to close the application.

## Supported arithmetic operations

| Operation | Command | Example | Expected result |
|---|---|---|---|
| Addition | `add` | `add 5 3` | 8 |
| Subtraction | `subtract` | `subtract 10 4` | 6 |
| Multiplication | `multiply` | `multiply 3 4` | 12 |
| Division | `divide` | `divide 10 2` | 5 |
| Exponentiation | `power` | `power 2 3` | 8 |
| Root | `root` | `root 27 3` | 3 |
| Modulus | `modulus` | `modulus 10 3` | 1 |
| Integer division | `int_divide` | `int_divide 10 3` | 3 |
| Percentage | `percent` | `percent 25 200` | 12.5 |
| Absolute difference | `abs_diff` | `abs_diff 5 12` | 7 |

The four additional midterm operations are modulus, integer division, percentage, and absolute difference.

## Interactive commands

Enter calculations in the format `operation number1 number2`.

```text
Enter command: add 5 3
Result: 8.0
```

| Command | Purpose |
|---|---|
| `help` | Show calculator instructions |
| `history` | Display stored calculation history |
| `clear` | Clear the history |
| `undo` | Restore the previous history state |
| `redo` | Reapply the last undone history change |
| `save` | Save history to CSV |
| `load` | Load history from CSV |
| `exit` | Exit the calculator |

The REPL handles supported calculation and file-operation errors without exiting unexpectedly. Ctrl+C and Ctrl+D also exit gracefully.

## Environment configuration

Configuration is loaded by `CalculatorConfig` in `app/calculator_config.py`, using `python-dotenv`. The `.env.example` file documents the available variables:

| Variable | Default | Purpose |
|---|---|---|
| `CALCULATOR_BASE_DIR` | `.` | Base directory for relative paths |
| `CALCULATOR_LOG_DIR` | `logs` | Directory for logs |
| `CALCULATOR_LOG_FILE` | `calculator.log` | Log filename |
| `CALCULATOR_HISTORY_DIR` | `.` | Directory for CSV history |
| `CALCULATOR_HISTORY_FILE` | `history.csv` | History filename |
| `CALCULATOR_MAX_HISTORY_SIZE` | `100` | Maximum number of history entries |
| `CALCULATOR_AUTO_SAVE` | `true` | Enable or disable auto-save |
| `CALCULATOR_PRECISION` | `2` | Decimal places in returned results |
| `CALCULATOR_MAX_INPUT_VALUE` | `1000000` | Maximum absolute numeric input |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | Configured text encoding |

Configuration validation requires a positive maximum history size, precision between 0 and 15, a positive finite input limit, `true` or `false` for auto-save, and a recognized encoding. It also checks configured file paths and creates necessary parent directories. Invalid settings raise `ConfigurationError`.

## Calculation history and CSV persistence

History is managed using a pandas DataFrame. Saved CSV records include five columns:

```text
operation,a,b,result,timestamp
```

The calculator saves and loads history using the configured CSV path. When restoring a CSV, the application validates operations, numeric values, timestamps, and recorded results before replacing existing history. Legacy four-column CSV files without timestamps are also supported by assigning an import timestamp. Invalid files raise `HistoryError` without replacing the current history.

With auto-save enabled, history updates trigger CSV saving through `AutoSaveObserver`, including changes caused by Undo and Redo.

## Logging and error handling

The application configures Python's `logging` module in `app/logger.py`. The default log location is `logs/calculator.log`.

- **INFO:** Successful calculations and history updates
- **WARNING:** Invalid inputs and values exceeding configured limits
- **ERROR:** Calculation failures, with exception details

The calculator validates operation names and numeric inputs and handles supported calculation failures, including division by zero. The REPL displays successful results in green and handled errors in red using Colorama.

## Software design patterns

- **Factory:** `OperationFactory` creates operation objects based on the requested operation.
- **Strategy:** Separate arithmetic operation classes implement interchangeable calculation behaviors.
- **Observer:** `HistoryObserver`, `AutoSaveObserver`, and `LoggingObserver` respond to history updates.
- **Memento:** `MementoManager` preserves and restores history states for Undo and Redo.
- **Facade:** `Calculator` offers a simplified interface to configuration, calculations, history, logging, and the REPL.

## Testing and coverage

Run the complete test suite:

```bash
python -m pytest -v
```

The tests cover arithmetic operations, input and configuration validation, history persistence, observers, logging, Undo/Redo, and REPL error recovery. The most recent local test run completed with **151 passing tests and 100% statement coverage**. The project is configured to enforce a 100% coverage threshold.

## Continuous integration

The GitHub Actions workflow in `.github/workflows/` is configured to run on pushes and pull requests involving `main` and `midterm-revision`. It uses Ubuntu and Python 3.13, installs dependencies from `requirements.txt`, runs pytest, and checks for 100% coverage.

The updated workflow must be pushed to GitHub and complete successfully before its remote CI status can be considered verified.

## Midterm enhancements

This project builds on the earlier Advanced Python Calculator with four additional arithmetic operations, improved configuration validation, timestamped CSV history restoration, file-based logging, expanded input error recovery, color-coded REPL output, and comprehensive automated tests. Incremental improvements are documented in the repository's Git commit history.
