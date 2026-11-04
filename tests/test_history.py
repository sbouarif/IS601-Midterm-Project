from datetime import datetime

import pandas as pd
import pytest

from app.calculation import Calculation
from app.exceptions import HistoryError
from app.history import History, AutoSaveObserver


@pytest.fixture
def history():
    """Create a fresh history for each test."""
    return History(max_size=3)


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", 5, 3, 8),
        ("subtract", 10, 4, 6),
        ("multiply", 3, 4, 12),
    ],
)
def test_add_calculation(history, operation, a, b, expected):
    calculation = Calculation(operation, a, b)
    history.add_calculation(calculation)

    data = history.get_history()

    assert len(data) == 1
    assert data.iloc[0]["operation"] == operation
    assert data.iloc[0]["result"] == expected


def test_history_max_size(history):
    """History should keep only the most recent calculations."""
    history.add_calculation(Calculation("add", 1, 1))
    history.add_calculation(Calculation("add", 2, 2))
    history.add_calculation(Calculation("add", 3, 3))
    history.add_calculation(Calculation("add", 4, 4))

    data = history.get_history()

    assert len(data) == 3
    assert data.iloc[0]["result"] == 4
    assert data.iloc[-1]["result"] == 8


def test_clear_history(history):
    history.add_calculation(Calculation("add", 5, 5))
    history.clear()

    assert history.get_history().empty


def test_get_history_returns_copy(history):
    history.add_calculation(Calculation("add", 2, 3))

    copied_history = history.get_history()
    copied_history.loc[0, "result"] = 100

    assert history.get_history().iloc[0]["result"] == 5


def test_save_and_load_csv(history, tmp_path):
    """History should persist using a CSV file."""
    filename = tmp_path / "history.csv"

    history.add_calculation(Calculation("add", 5, 3))
    history.save_to_csv(filename)

    new_history = History()
    new_history.load_from_csv(filename)

    data = new_history.get_history()

    assert len(data) == 1
    assert data.iloc[0]["operation"] == "add"
    assert data.iloc[0]["result"] == 8


def test_add_observer(history):
    class TestObserver:
        def __init__(self):
            self.called = False

        def update(self, updated_history):
            self.called = True
            assert updated_history is history

    observer = TestObserver()
    history.add_observer(observer)
    history.add_calculation(Calculation("add", 1, 2))

    assert observer.called is True


def test_auto_save_observer(history, tmp_path):
    filename = tmp_path / "auto_history.csv"

    observer = AutoSaveObserver(filename)
    history.add_observer(observer)
    history.add_calculation(Calculation("multiply", 4, 5))

    assert filename.exists()

    saved_data = pd.read_csv(filename)
    assert saved_data.iloc[0]["result"] == 20


def test_clear_notifies_observer(history):
    class TestObserver:
        def __init__(self):
            self.called = False

        def update(self, updated_history):
            self.called = True

    observer = TestObserver()
    history.add_observer(observer)
    history.clear()

    assert observer.called is True


def test_save_error(history, monkeypatch):
    def raise_error(*args, **kwargs):
        raise OSError("Save failed")

    monkeypatch.setattr(pd.DataFrame, "to_csv", raise_error)

    with pytest.raises(HistoryError, match="Unable to save history"):
        history.save_to_csv("history.csv")


def test_load_error(history, monkeypatch):
    def raise_error(*args, **kwargs):
        raise OSError("Load failed")

    monkeypatch.setattr(pd, "read_csv", raise_error)

    with pytest.raises(HistoryError, match="Unable to load history"):
        history.load_from_csv("history.csv")


def test_timestamp_preserved_after_csv_round_trip(tmp_path):
    """Saving and loading must preserve the original timestamp."""
    original_timestamp = datetime(2026, 10, 15, 14, 30, 45)

    history = History()
    calculation = Calculation(
        "add", 10, 5, timestamp=original_timestamp
    )
    history.add_calculation(calculation)

    filename = tmp_path / "timestamped_history.csv"
    history.save_to_csv(filename)

    restored_history = History()
    restored_history.load_from_csv(filename)

    restored = restored_history.get_history()

    assert len(restored) == 1
    assert restored.iloc[0]["timestamp"] == (
        original_timestamp.isoformat()
    )
    assert restored.iloc[0]["result"] == 15


def test_csv_contains_required_columns(tmp_path):
    """CSV files must contain all five required fields."""
    history = History()
    history.add_calculation(Calculation("multiply", 4, 5))

    filename = tmp_path / "history.csv"
    history.save_to_csv(filename)

    saved = pd.read_csv(filename)

    assert list(saved.columns) == [
        "operation", "a", "b", "result", "timestamp"
    ]


def test_malformed_csv_preserves_existing_history(tmp_path):
    """Invalid CSV must not destroy previously stored history."""
    history = History()
    history.add_calculation(Calculation("add", 2, 3))

    original = history.get_history()

    filename = tmp_path / "invalid.csv"
    filename.write_text("invalid,column\n1,2\n")

    with pytest.raises(HistoryError, match="Unable to load history"):
        history.load_from_csv(filename)

    pd.testing.assert_frame_equal(
        history.get_history(),
        original,
    )


def test_invalid_timestamp_rejected(tmp_path):
    """Reject history files containing invalid timestamps."""
    filename = tmp_path / "invalid_timestamp.csv"

    pd.DataFrame(
        [{
            "operation": "add",
            "a": 2,
            "b": 3,
            "result": 5,
            "timestamp": "not-a-date",
        }]
    ).to_csv(filename, index=False)

    history = History()

    with pytest.raises(HistoryError, match="Unable to load history"):
        history.load_from_csv(filename)


def test_loaded_history_respects_max_size(tmp_path):
    """Restored history must respect the configured maximum size."""
    original = History(max_size=10)

    for number in range(5):
        original.add_calculation(
            Calculation("add", number, 1)
        )

    filename = tmp_path / "history.csv"
    original.save_to_csv(filename)

    restored = History(max_size=3)
    restored.load_from_csv(filename)

    data = restored.get_history()

    assert len(data) == 3
    assert list(data["result"]) == [3, 4, 5]

def test_invalid_operation_in_csv_rejected(tmp_path):
    """Reject CSV records containing unsupported operations."""
    filename = tmp_path / "invalid_operation.csv"

    pd.DataFrame(
        [{
            "operation": "not_an_operation",
            "a": 5,
            "b": 3,
            "result": 8,
            "timestamp": "2026-10-15T14:30:45",
        }]
    ).to_csv(filename, index=False)

    history = History()

    with pytest.raises(HistoryError, match="Unable to load history"):
        history.load_from_csv(filename)

@pytest.mark.parametrize("invalid_value", ["nan", "inf", "-inf"])
def test_nonfinite_csv_numbers_rejected(tmp_path, invalid_value):
    """Reject CSV history containing nonfinite numeric values."""
    filename = tmp_path / "invalid_number.csv"

    pd.DataFrame(
        [{
            "operation": "add",
            "a": invalid_value,
            "b": 3,
            "result": 8,
            "timestamp": "2026-10-15T14:30:45",
        }]
    ).to_csv(filename, index=False)

    history = History()

    with pytest.raises(HistoryError, match="Unable to load history"):
        history.load_from_csv(filename)

def test_incorrect_csv_result_rejected(tmp_path):
    """Reject saved calculations whose results are incorrect."""
    filename = tmp_path / "incorrect_result.csv"

    pd.DataFrame(
        [{
            "operation": "add",
            "a": 5,
            "b": 3,
            "result": 100,
            "timestamp": "2026-10-15T14:30:45",
        }]
    ).to_csv(filename, index=False)

    history = History()

    with pytest.raises(HistoryError, match="Unable to load history"):
        history.load_from_csv(filename)