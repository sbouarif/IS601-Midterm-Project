import pandas as pd
import pytest

from app.calculator_memento import CalculatorMemento, MementoManager


@pytest.fixture
def sample_state():
    return pd.DataFrame(
        [
            {
                "operation": "add",
                "a": 5,
                "b": 3,
                "result": 8,
            }
        ]
    )


def test_memento_stores_copy(sample_state):
    memento = CalculatorMemento(sample_state)

    sample_state.loc[0, "result"] = 100

    assert memento.state.loc[0, "result"] == 8


def test_save_state(sample_state):
    manager = MementoManager()
    manager.save_state(sample_state)

    assert len(manager.undo_stack) == 1
    assert len(manager.redo_stack) == 0


def test_save_state_clears_redo(sample_state):
    manager = MementoManager()

    manager.redo_stack.append(CalculatorMemento(sample_state))
    manager.save_state(sample_state)

    assert len(manager.redo_stack) == 0


def test_undo(sample_state):
    manager = MementoManager()

    empty_state = pd.DataFrame()
    manager.save_state(empty_state)

    restored = manager.undo(sample_state)

    assert restored.empty
    assert len(manager.redo_stack) == 1


def test_undo_with_empty_stack(sample_state):
    manager = MementoManager()

    restored = manager.undo(sample_state)

    assert restored.equals(sample_state)


def test_redo(sample_state):
    manager = MementoManager()

    empty_state = pd.DataFrame()
    manager.save_state(empty_state)

    restored = manager.undo(sample_state)
    redone = manager.redo(restored)

    assert redone.equals(sample_state)
    assert len(manager.undo_stack) == 1


def test_redo_with_empty_stack(sample_state):
    manager = MementoManager()

    restored = manager.redo(sample_state)

    assert restored.equals(sample_state)