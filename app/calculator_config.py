import codecs
import math
import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


class CalculatorConfig:
    """Load and validate calculator configuration settings."""

    def __init__(self):
        load_dotenv()

        self.base_dir = Path(
            os.getenv("CALCULATOR_BASE_DIR", ".")
        ).expanduser()

        self.log_dir = self._resolve_path(
            os.getenv("CALCULATOR_LOG_DIR", "logs")
        )
        self.history_dir = self._resolve_path(
            os.getenv("CALCULATOR_HISTORY_DIR", ".")
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
        except (ValueError, OverflowError) as exc:
            raise ConfigurationError(
                "Invalid numeric configuration value."
            ) from exc

        auto_save_value = os.getenv(
            "CALCULATOR_AUTO_SAVE", "true"
        ).strip().lower()

        if auto_save_value not in ("true", "false"):
            raise ConfigurationError(
                "CALCULATOR_AUTO_SAVE must be true or false."
            )

        self.auto_save = auto_save_value == "true"

        self.default_encoding = os.getenv(
            "CALCULATOR_DEFAULT_ENCODING", "utf-8"
        ).strip()

        self.log_file = self._resolve_file(
            os.getenv("CALCULATOR_LOG_FILE", "calculator.log"),
            self.log_dir,
        )
        self.history_file = self._resolve_file(
            os.getenv("CALCULATOR_HISTORY_FILE", "history.csv"),
            self.history_dir,
        )

        self.validate()

    def _resolve_path(self, value):
        """Resolve relative paths against the base directory."""
        path = Path(value).expanduser()
        return path if path.is_absolute() else self.base_dir / path

    def _resolve_file(self, value, directory):
        """Resolve a filename relative to its configured directory."""
        path = Path(value).expanduser()
        return path if path.is_absolute() else directory / path

    def validate(self):
        """Validate configuration and prepare output directories."""
        if self.max_history_size <= 0:
            raise ConfigurationError(
                "Maximum history size must be greater than zero."
            )

        if not 0 <= self.precision <= 15:
            raise ConfigurationError(
                "Precision must be between 0 and 15."
            )

        if (
            not math.isfinite(self.max_input_value)
            or self.max_input_value <= 0
        ):
            raise ConfigurationError(
                "Maximum input value must be a positive finite number."
            )

        try:
            codecs.lookup(self.default_encoding)
        except LookupError as exc:
            raise ConfigurationError(
                "Invalid file encoding."
            ) from exc

        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ConfigurationError(
                "Unable to create configured directories."
            ) from exc

        if self.log_file.is_dir() or self.history_file.is_dir():
            raise ConfigurationError(
                "Configured file paths must refer to files."
            )
