import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def test_default_config(monkeypatch):
    """Test the default configuration values."""
    variables = [
        "CALCULATOR_BASE_DIR",
        "CALCULATOR_MAX_HISTORY_SIZE",
        "CALCULATOR_AUTO_SAVE",
        "CALCULATOR_PRECISION",
        "CALCULATOR_MAX_INPUT_VALUE",
        "CALCULATOR_DEFAULT_ENCODING",
    ]

    for variable in variables:
        monkeypatch.delenv(variable, raising=False)

    config = CalculatorConfig()

    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 2
    assert config.max_input_value == 1000000
    assert config.default_encoding == "utf-8"


def test_custom_config(monkeypatch, tmp_path):
    """Test configuration values from environment variables."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "50")
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_PRECISION", "4")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "5000")
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "ascii")

    config = CalculatorConfig()

    assert config.base_dir == tmp_path
    assert config.max_history_size == 50
    assert config.auto_save is False
    assert config.precision == 4
    assert config.max_input_value == 5000
    assert config.default_encoding == "ascii"
    assert config.history_file == tmp_path / "history.csv"


@pytest.mark.parametrize(
    "variable,value",
    [
        ("CALCULATOR_MAX_HISTORY_SIZE", "abc"),
        ("CALCULATOR_PRECISION", "abc"),
        ("CALCULATOR_MAX_INPUT_VALUE", "abc"),
    ],
)
def test_invalid_numeric_config(monkeypatch, variable, value):
    monkeypatch.setenv(variable, value)

    with pytest.raises(
        ConfigurationError,
        match="Invalid numeric configuration value",
    ):
        CalculatorConfig()


@pytest.mark.parametrize(
    "variable,value,error_message",
    [
        (
            "CALCULATOR_MAX_HISTORY_SIZE",
            "0",
            "Maximum history size must be greater than zero",
        ),
        (
            "CALCULATOR_PRECISION",
            "-1",
            "Precision must be between 0 and 15",
        ),
        (
            "CALCULATOR_MAX_INPUT_VALUE",
            "0",
            "Maximum input value must be a positive finite number",
        ),
    ],
)
def test_invalid_config_values(
    monkeypatch,
    variable,
    value,
    error_message,
):
    monkeypatch.setenv(variable, value)

    with pytest.raises(ConfigurationError, match=error_message):
        CalculatorConfig()

@pytest.mark.parametrize(
    "value",
    ["yes", "no", "1", "0", "maybe", ""],
)
def test_invalid_auto_save(monkeypatch, value):
    """Reject unsupported auto-save configuration values."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)

    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_AUTO_SAVE must be true or false",
    ):
        CalculatorConfig()


@pytest.mark.parametrize(
    "variable,value",
    [
        ("CALCULATOR_MAX_HISTORY_SIZE", "-5"),
        ("CALCULATOR_PRECISION", "16"),
        ("CALCULATOR_MAX_INPUT_VALUE", "-100"),
        ("CALCULATOR_MAX_INPUT_VALUE", "nan"),
        ("CALCULATOR_MAX_INPUT_VALUE", "inf"),
        ("CALCULATOR_MAX_INPUT_VALUE", "-inf"),
    ],
)
def test_invalid_configuration_ranges(monkeypatch, variable, value):
    """Reject values outside supported configuration ranges."""
    monkeypatch.setenv(variable, value)

    with pytest.raises(ConfigurationError):
        CalculatorConfig()


def test_invalid_encoding(monkeypatch):
    """Reject unknown file encodings."""
    monkeypatch.setenv(
        "CALCULATOR_DEFAULT_ENCODING",
        "not-a-real-encoding",
    )

    with pytest.raises(
        ConfigurationError,
        match="Invalid file encoding",
    ):
        CalculatorConfig()


def test_custom_directories_and_files(monkeypatch, tmp_path):
    """Verify custom log and history paths are respected."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_LOG_DIR", "my_logs")
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", "my_history")
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "operations.log")
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "calculations.csv")

    config = CalculatorConfig()

    assert config.log_dir == tmp_path / "my_logs"
    assert config.history_dir == tmp_path / "my_history"
    assert config.log_file == tmp_path / "my_logs" / "operations.log"
    assert (
        config.history_file
        == tmp_path / "my_history" / "calculations.csv"
    )

    assert config.log_file.parent.is_dir()
    assert config.history_file.parent.is_dir()


def test_absolute_file_paths(monkeypatch, tmp_path):
    """Verify absolute file paths override configured directories."""
    log_path = tmp_path / "absolute.log"
    history_path = tmp_path / "absolute.csv"

    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(log_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(history_path))

    config = CalculatorConfig()

    assert config.log_file == log_path
    assert config.history_file == history_path


def test_configured_file_cannot_be_directory(monkeypatch, tmp_path):
    """Reject a directory used as a log file path."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(tmp_path))

    with pytest.raises(
        ConfigurationError,
        match="Configured file paths must refer to files",
    ):
        CalculatorConfig()


def test_directory_creation_failure(monkeypatch, tmp_path):
    """Handle a configured directory blocked by an existing file."""
    blocking_file = tmp_path / "blocked"
    blocking_file.write_text("not a directory")

    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_LOG_DIR", "blocked/subdirectory")

    with pytest.raises(
        ConfigurationError,
        match="Unable to create configured directories",
    ):
        CalculatorConfig()