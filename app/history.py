import math
from pathlib import Path

import pandas as pd

from app.calculation import Calculation
from app.exceptions import CalculatorError, HistoryError
from app.operations import OperationFactory
from datetime import datetime


HISTORY_COLUMNS = ["operation", "a", "b", "result", "timestamp"]


class HistoryObserver:
    """Observer interface for calculation history events."""

    def update(self, history):
        """React to a change in calculation history."""
        raise NotImplementedError


class AutoSaveObserver(HistoryObserver):
    """Automatically save history whenever it changes."""

    def __init__(self, filename):
        self.filename = filename

    def update(self, history):
        history.save_to_csv(self.filename)

class LoggingObserver(HistoryObserver):
    """Log changes to calculation history."""

    def __init__(self, logger):
        self.logger = logger

    def update(self, history):
        """Record a history update in the application log."""
        self.logger.info(
            "Calculation history updated. Total entries: %s",
            len(history.get_history()),
        )

class History:
    """Manage timestamped calculation history using pandas."""

    def __init__(self, max_size=100):
        self.max_size = max_size
        self.data = pd.DataFrame(columns=HISTORY_COLUMNS)
        self.observers = []

    def add_observer(self, observer):
        """Register an observer for history changes."""
        self.observers.append(observer)

    def notify_observers(self):
        """Notify registered observers."""
        for observer in self.observers:
            observer.update(self)

    def add_calculation(self, calculation):
        """Add a completed Calculation to history."""
        if not isinstance(calculation, Calculation):
            raise HistoryError("History requires a Calculation object.")

        new_row = pd.DataFrame([calculation.to_dict()])

        self.data = pd.concat(
            [self.data, new_row],
            ignore_index=True,
        )

        if len(self.data) > self.max_size:
            self.data = (
                self.data.tail(self.max_size)
                .reset_index(drop=True)
            )

        self.notify_observers()

    def clear(self):
        """Remove all calculation history."""
        self.data = pd.DataFrame(columns=HISTORY_COLUMNS)
        self.notify_observers()

    def get_history(self):
        """Return a defensive copy of the history DataFrame."""
        return self.data.copy(deep=True)

    def save_to_csv(self, filename):
        """Save all history fields, including timestamps, to CSV."""
        try:
            path = Path(filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            self.data.to_csv(path, index=False)
        except (OSError, ValueError, UnicodeError) as exc:
            raise HistoryError("Unable to save history.") from exc

    def load_from_csv(self, filename):
        """Restore Calculation objects from CSV without losing history."""
        try:
            loaded = pd.read_csv(filename)

            legacy_columns = ["operation", "a", "b", "result"]
            if list(loaded.columns) == legacy_columns:
                # Older history files did not include timestamps.
                # Assign an import timestamp to legacy records.
                loaded["timestamp"] = datetime.now().isoformat()
                
            elif list(loaded.columns) != HISTORY_COLUMNS:
                raise ValueError(
                    "CSV must contain operation, a, b, result, timestamp."
                )

            restored_calculations = []

            for _, row in loaded.iterrows():
                operation = str(row["operation"])
                
                try:
                    OperationFactory.create_operation(operation)
                except (ValueError, KeyError, CalculatorError) as exc:
                    raise ValueError(
                        f"Unsupported operation in CSV: {operation}"
                    ) from exc
                a = float(row["a"])
                b = float(row["b"])
                result = float(row["result"])

                if not all(math.isfinite(value) for value in (a, b, result)):
                    raise ValueError(
                        "CSV contains NaN or infinite numeric values."
                    )

                timestamp = pd.to_datetime(
                    row["timestamp"],
                    errors="raise",
                ).to_pydatetime()

                calculation = Calculation(
                    operation,
                    a,
                    b,
                    timestamp=timestamp,
                )
                
                try:
                    expected_result = calculation.perform()
                except (CalculatorError, ValueError, ArithmeticError) as exc:
                    raise ValueError(
                        f"Invalid calculation in CSV: {operation}"
                    ) from exc 
                
                if not math.isclose(
                    result,
                    expected_result,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    raise ValueError(
                        f"Incorrect result in CSV for {operation}: "
                        f"expected {expected_result}, found {result}"
                    )
                restored_calculations.append(calculation)

            restored_rows = [
                calculation.to_dict()
                for calculation in restored_calculations
            ]

            restored_data = pd.DataFrame(
                restored_rows,
                columns=HISTORY_COLUMNS,
            )

            self.data = (
                restored_data.tail(self.max_size)
                .reset_index(drop=True)
            )

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            OverflowError,
            UnicodeError,
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
        ) as exc:
            raise HistoryError(
                f"Unable to load history: {exc}"
            ) from exc