import pandas as pd

from app.exceptions import HistoryError


class HistoryObserver:
    """Observer interface for calculation history events."""

    def update(self, history):
        """React to a change in calculation history."""
        pass  # pragma: no cover


class AutoSaveObserver(HistoryObserver):
    """Automatically saves history when it changes."""

    def __init__(self, filename):
        self.filename = filename

    def update(self, history):
        history.save_to_csv(self.filename)


class History:
    """Manages calculator history using a pandas DataFrame."""

    def __init__(self, max_size=100):
        self.max_size = max_size
        self.data = pd.DataFrame(
            columns=["operation", "a", "b", "result"]
        )
        self.observers = []

    def add_observer(self, observer):
        """Add an observer to the history."""
        self.observers.append(observer)

    def notify_observers(self):
        """Notify observers that history has changed."""
        for observer in self.observers:
            observer.update(self)

    def add_calculation(self, calculation):
        """Add a calculation to history."""
        new_row = pd.DataFrame([calculation.to_dict()])
        self.data = pd.concat(
            [self.data, new_row],
            ignore_index=True,
        )

        if len(self.data) > self.max_size:
            self.data = self.data.tail(self.max_size).reset_index(drop=True)

        self.notify_observers()

    def clear(self):
        """Clear all calculation history."""
        self.data = self.data.iloc[0:0]
        self.notify_observers()

    def get_history(self):
        """Return the calculation history."""
        return self.data.copy()

    def save_to_csv(self, filename):
        """Save calculation history to a CSV file."""
        try:
            self.data.to_csv(filename, index=False)
        except (OSError, PermissionError) as exc:
            raise HistoryError("Unable to save history.") from exc

    def load_from_csv(self, filename):
        """Load calculation history from a CSV file."""
        try:
            self.data = pd.read_csv(filename)
        except (OSError, pd.errors.ParserError) as exc:
            raise HistoryError("Unable to load history.") from exc