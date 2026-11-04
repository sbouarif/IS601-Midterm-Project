import pytest

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
