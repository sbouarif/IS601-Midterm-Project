from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import MementoManager
from app.exceptions import CalculatorError
from app.history import History, AutoSaveObserver
from app.input_validators import validate_number, validate_operation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Calculator:
    """Facade that provides a simple interface to the calculator system."""

    def __init__(self):
        self.config = CalculatorConfig()
        self.history = History(self.config.max_history_size)
        self.memento_manager = MementoManager()

        if self.config.auto_save:
            self.history.add_observer(
                AutoSaveObserver(self.config.history_file)
            )

        if self.config.history_file.exists():
            self.history.load_from_csv(self.config.history_file)

    def calculate(self, operation, a, b):
        """Validate input, perform a calculation, and store it."""
        operation = validate_operation(operation)
        a = validate_number(a)
        b = validate_number(b)

        # LBYL: check values before performing the calculation.
        if abs(a) > self.config.max_input_value:
            raise ValueError("First number exceeds maximum input value.")

        if abs(b) > self.config.max_input_value:
            raise ValueError("Second number exceeds maximum input value.")

        self.memento_manager.save_state(
            self.history.get_history()
        )

        calculation = Calculation(operation, a, b)
        try:
            result = calculation.perform()
        except Exception:
            logger.exception(
                "Calculation failed: %s(%s, %s)",
                operation, a, b
            )
            raise
        logger.info(
            "Calculation completed: %s(%s, %s) = %s",
            operation, a, b, result
        )

        self.history.add_calculation(calculation)

        return round(result, self.config.precision)

    def show_history(self):
        """Return the current calculation history."""
        return self.history.get_history()

    def clear_history(self):
        """Clear calculation history."""
        self.memento_manager.save_state(
            self.history.get_history()
        )
        self.history.clear()

    def undo(self):
        """Undo the last history change."""
        current = self.history.get_history()
        self.history.data = self.memento_manager.undo(current)

    def redo(self):
        """Redo the last undone history change."""
        current = self.history.get_history()
        self.history.data = self.memento_manager.redo(current)

    def save(self):
        """Save history to the configured CSV file."""
        self.history.save_to_csv(self.config.history_file)

    def load(self):
        """Load history from the configured CSV file."""
        self.history.load_from_csv(self.config.history_file)

    @staticmethod
    def display_help():
        """Display available calculator commands."""
        print("Available operations:")
        print("  add, subtract, multiply, divide, power, root")
        print("Format: operation number1 number2")
        print("Example: add 5 3")
        print("Commands:")
        print("  help, history, clear, undo, redo, save, load, exit")

    def start(self):
        """Start the calculator REPL."""
        print("Welcome to the Advanced Calculator!")
        print("Type 'help' for instructions or 'exit' to quit.")

        while True:
            command = input("Enter command: ").strip()

            if command == "exit":
                print("Goodbye!")
                break

            if command == "help":
                self.display_help()
                continue

            if command == "history":
                print(self.show_history().to_string(index=False))
                continue

            if command == "clear":
                self.clear_history()
                print("History cleared.")
                continue

            if command == "undo":
                self.undo()
                print("Undo complete.")
                continue

            if command == "redo":
                self.redo()
                print("Redo complete.")
                continue

            if command == "save":
                self.save()
                print("History saved.")
                continue

            if command == "load":
                self.load()
                print("History loaded.")
                continue

            try:
                parts = command.split()

                if len(parts) != 3:
                    raise ValueError(
                        "Enter an operation followed by two numbers."
                    )

                operation, a, b = parts
                result = self.calculate(operation, a, b)
                print(f"Result: {result}")

            # EAFP: attempt the operation and handle errors if they occur.
            except (CalculatorError, ValueError, ZeroDivisionError) as exc:
                print(f"Error: {exc}")