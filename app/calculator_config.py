import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


class CalculatorConfig:
    """Manages calculator configuration settings."""

    def __init__(self):
        load_dotenv()

        self.base_dir = Path(
            os.getenv("CALCULATOR_BASE_DIR", ".")
        )

        try:
            self.max_history_size = int(
                os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "100")
            )
            self.precision = int(
                os.getenv("CALCULATOR_PRECISION", "2")
            )
            self.max_input_value = float(
                os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1000000")
            )
        except ValueError as exc:
            raise ConfigurationError(
                "Invalid numeric configuration value."
            ) from exc

        self.auto_save = (
            os.getenv("CALCULATOR_AUTO_SAVE", "true").lower() == "true"
        )

        self.default_encoding = os.getenv(
            "CALCULATOR_DEFAULT_ENCODING",
            "utf-8",
        )

        self.validate()

    def validate(self):
        """Validate configuration values."""
        if self.max_history_size <= 0:
            raise ConfigurationError(
                "Maximum history size must be greater than zero."
            )

        if self.precision < 0:
            raise ConfigurationError(
                "Precision cannot be negative."
            )

        if self.max_input_value <= 0:
            raise ConfigurationError(
                "Maximum input value must be greater than zero."
            )

    @property
    def history_file(self):
        """Return the path used for saved calculation history."""
        return self.base_dir / "history.csv"