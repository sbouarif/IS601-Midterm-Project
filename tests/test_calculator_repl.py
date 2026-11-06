import pytest
import pandas as pd

from app.calculator_repl import Calculator
from app.exceptions import InvalidInputError



@pytest.fixture
def calculator(monkeypatch, tmp_path):
    """Create a calculator with isolated test configuration."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "100")
    monkeypatch.setenv("CALCULATOR_PRECISION", "2")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "1000000")

    return Calculator()


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", "5", "3", 8.0),
        ("subtract", "10", "4", 6.0),
        ("multiply", "6", "7", 42.0),
        ("divide", "20", "4", 5.0),
        ("power", "2", "3", 8.0),
        ("root", "16", "2", 4.0),
    ],
)
def test_calculate(calculator, operation, a, b, expected):
    assert calculator.calculate(operation, a, b) == expected


def test_calculate_adds_to_history(calculator):
    calculator.calculate("add", "5", "3")

    history = calculator.show_history()

    assert len(history) == 1
    assert history.iloc[0]["operation"] == "add"
    assert history.iloc[0]["result"] == 8.0


@pytest.mark.parametrize(
    "a,b,message",
    [
        ("1000001", "1", "First number exceeds maximum input value"),
        ("1", "1000001", "Second number exceeds maximum input value"),
    ],
)
def test_max_input_value(calculator, a, b, message):
    with pytest.raises(ValueError, match=message):
        calculator.calculate("add", a, b)


def test_clear_history(calculator):
    calculator.calculate("add", "5", "3")
    calculator.clear_history()

    assert calculator.show_history().empty


def test_undo(calculator):
    calculator.calculate("add", "5", "3")
    calculator.undo()

    assert calculator.show_history().empty


def test_redo(calculator):
    calculator.calculate("add", "5", "3")
    calculator.undo()
    calculator.redo()

    assert len(calculator.show_history()) == 1


def test_save_and_load(calculator):
    calculator.calculate("multiply", "4", "5")
    calculator.save()

    calculator.clear_history()
    assert calculator.show_history().empty

    calculator.load()

    assert len(calculator.show_history()) == 1
    assert calculator.show_history().iloc[0]["result"] == 20


def test_auto_save_observer(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")

    calculator = Calculator()
    calculator.calculate("add", "2", "3")

    assert calculator.config.history_file.exists()


def test_load_existing_history(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")

    first_calculator = Calculator()
    first_calculator.calculate("add", "2", "3")
    first_calculator.save()

    second_calculator = Calculator()

    assert len(second_calculator.show_history()) == 1


def test_display_help(capsys):
    Calculator.display_help()

    output = capsys.readouterr().out

    assert "Available operations:" in output
    assert "help, history, clear, undo, redo, save, load, exit" in output

def test_repl_commands(calculator, monkeypatch, capsys):
    commands = iter(
        [
            "help",
            "add 5 3",
            "history",
            "undo",
            "redo",
            "save",
            "clear",
            "load",
            "exit",
        ]
    )

    monkeypatch.setattr("builtins.input", lambda _: next(commands))

    calculator.start()

    output = capsys.readouterr().out

    assert "Welcome to the Advanced Calculator!" in output
    assert "Available operations:" in output
    assert "Result: 8.0" in output
    assert "Undo complete." in output
    assert "Redo complete." in output
    assert "History saved." in output
    assert "History cleared." in output
    assert "History loaded." in output
    assert "Goodbye!" in output


@pytest.mark.parametrize(
    "command,error_text",
    [
        ("add 5", "Enter an operation followed by two numbers"),
        ("add hello 5", "Invalid number"),
        ("wrong 5 3", "Invalid operation"),
        ("divide 10 0", "Cannot divide by zero"),
    ],
)
def test_repl_errors(
    calculator,
    monkeypatch,
    capsys,
    command,
    error_text,
):
    commands = iter([command, "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(commands))

    calculator.start()

    output = capsys.readouterr().out

    assert "Error:" in output
    assert error_text in output

def test_successful_calculation_written_to_log(calculator):
    """Successful calculations should be recorded in the configured log file."""
    calculator.calculate("add", "5", "3")

    log_file = calculator.config.log_file

    assert log_file.exists()

    log_contents = log_file.read_text(encoding="utf-8")

    assert "INFO" in log_contents
    assert "Calculation completed: add(5.0, 3.0) = 8.0" in log_contents
    assert "Calculation history updated. Total entries: 1" in log_contents

def test_failed_calculation_written_to_log(calculator):
    """Failed calculations should produce an ERROR log entry."""
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        calculator.calculate("divide", "10", "0")

    log_file = calculator.config.log_file

    assert log_file.exists()

    log_contents = log_file.read_text(encoding="utf-8")

    assert "ERROR" in log_contents
    assert "Calculation failed: divide(10.0, 0.0)" in log_contents
    assert "ZeroDivisionError: Cannot divide by zero." in log_contents
    assert calculator.show_history().empty

def test_invalid_input_written_to_warning_log(calculator):
    """Invalid numeric input should produce a WARNING log entry."""
    with pytest.raises(InvalidInputError, match="Invalid number"):
        calculator.calculate("add", "hello", "5")

    log_contents = calculator.config.log_file.read_text(
        encoding="utf-8"
    )

    assert "WARNING" in log_contents
    assert "Invalid calculation input:" in log_contents
    assert calculator.show_history().empty  

def test_failed_calculation_does_not_create_undo_state(calculator):
    """A failed calculation must not create an undo checkpoint."""
    calculator.calculate("add", "5", "3")

    undo_count_before = len(calculator.memento_manager.undo_stack)

    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        calculator.calculate("divide", "10", "0")

    assert len(calculator.memento_manager.undo_stack) == undo_count_before
    assert len(calculator.show_history()) == 1

    calculator.undo()

    assert calculator.show_history().empty

@pytest.mark.parametrize(
    "a,b,expected_message",
    [
        ("1000001", "1", "First number exceeds maximum input value"),
        ("1", "1000001", "Second number exceeds maximum input value"),
    ],
)
def test_max_input_violation_written_to_warning_log(
    calculator, a, b, expected_message
):
    """Exceeding the input limit should produce a WARNING log."""
    with pytest.raises(ValueError, match=expected_message):
        calculator.calculate("add", a, b)

    log_contents = calculator.config.log_file.read_text(
        encoding="utf-8"
    )

    assert "WARNING" in log_contents
    assert expected_message in log_contents
    assert calculator.show_history().empty

def test_repl_recovers_from_failed_load(calculator, monkeypatch, capsys):
    """A failed CSV load should not terminate the calculator."""
    commands = iter(["load", "add 5 3", "exit"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(commands)
    )

    def failed_load():
        raise OSError("Unable to read history file.")

    monkeypatch.setattr(calculator, "load", failed_load)

    calculator.start()

    output = capsys.readouterr().out

    assert "Error: Unable to read history file." in output
    assert "Result: 8.0" in output
    assert "Goodbye!" in output
    assert len(calculator.show_history()) == 1

def test_repl_recovers_from_failed_save(calculator, monkeypatch, capsys):
    """A failed CSV save should not terminate the calculator."""
    commands = iter(["save", "add 5 3", "exit"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(commands)
    )

    def failed_save():
        raise OSError("Unable to write history file.")

    monkeypatch.setattr(calculator, "save", failed_save)

    calculator.start()

    output = capsys.readouterr().out

    assert "Error: Unable to write history file." in output
    assert "Result: 8.0" in output
    assert "Goodbye!" in output
    assert len(calculator.show_history()) == 1

@pytest.mark.parametrize(
    "interruption",
    [EOFError, KeyboardInterrupt],
)
def test_repl_exits_gracefully_on_interruption(
    calculator, monkeypatch, capsys, interruption
):
    """The REPL should exit without crashing when input is interrupted."""

    def interrupted_input(prompt):
        raise interruption()

    monkeypatch.setattr("builtins.input", interrupted_input)

    calculator.start()

    output = capsys.readouterr().out

    assert "Goodbye!" in output

def test_undo_redo_updates_autosaved_csv(tmp_path, monkeypatch):
    """Undo and Redo should synchronize the auto-saved CSV file."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")

    calculator = Calculator()

    calculator.calculate("add", "5", "3")
    calculator.calculate("multiply", "4", "2")

    csv_file = calculator.config.history_file

    assert csv_file.exists()
    assert len(pd.read_csv(csv_file)) == 2

    calculator.undo()

    assert len(calculator.show_history()) == 1
    assert len(pd.read_csv(csv_file)) == 1

    calculator.redo()

    assert len(calculator.show_history()) == 2
    assert len(pd.read_csv(csv_file)) == 2

def test_complex_result_rejected(calculator):
    with pytest.raises(
        ValueError,
        match="finite real number"
    ):
        calculator.calculate("power", -8, 0.5)


def test_zero_negative_power_rejected(calculator):
    with pytest.raises(ZeroDivisionError):
        calculator.calculate("root", 0, -2)

def test_startup_recovers_from_corrupted_history(monkeypatch, tmp_path, capsys):
    """Calculator should start even when saved history is invalid."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")

    history_file = tmp_path / "history.csv"
    history_file.write_text(
        "operation,a,b,result,timestamp\n"
        "add,5,3,(15+0j),2026-11-04T12:00:00\n",
        encoding="utf-8",
    )

    calculator = Calculator()

    output = capsys.readouterr().out

    assert "Warning: Saved history could not be loaded" in output
    assert calculator.show_history().empty
    assert history_file.exists()

    assert calculator.calculate("add", 5, 3) == 8.0

@pytest.mark.parametrize("command", ["clear", "undo", "redo"])
def test_repl_recovers_from_history_command_error(
    calculator, monkeypatch, capsys, command
):
    """History command failures should not terminate the REPL."""
    commands = iter([command, "add 5 3", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(commands))

    def failed_history_command():
        raise OSError("Simulated history storage failure.")

    method_name = {
        "clear": "clear_history",
        "undo": "undo",
        "redo": "redo",
    }[command]

    monkeypatch.setattr(calculator, method_name, failed_history_command)

    calculator.start()

    output = capsys.readouterr().out

    assert "Error: Simulated history storage failure." in output
    assert "Result: 8.0" in output
    assert "Goodbye!" in output

    log_contents = calculator.config.log_file.read_text(
        encoding="utf-8"
    )
    assert "History command failed: Simulated history storage failure." in log_contents