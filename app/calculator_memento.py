class CalculatorMemento:
    """Stores a snapshot of calculator history."""

    def __init__(self, state):
        self.state = state.copy(deep=True)


class MementoManager:
    """Manages calculator history states for undo and redo."""

    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self, state):
        """Save the current state."""
        self.undo_stack.append(CalculatorMemento(state))
        self.redo_stack.clear()

    def undo(self, current_state):
        """Restore the previous state."""
        if not self.undo_stack:
            return current_state

        self.redo_stack.append(CalculatorMemento(current_state))
        memento = self.undo_stack.pop()
        return memento.state.copy(deep=True)

    def redo(self, current_state):
        """Restore a previously undone state."""
        if not self.redo_stack:
            return current_state

        self.undo_stack.append(CalculatorMemento(current_state))
        memento = self.redo_stack.pop()
        return memento.state.copy(deep=True)