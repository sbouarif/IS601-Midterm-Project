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
            "Precision cannot be negative",
        ),
        (
            "CALCULATOR_MAX_INPUT_VALUE",
            "0",
            "Maximum input value must be greater than zero",
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