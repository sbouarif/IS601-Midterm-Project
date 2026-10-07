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