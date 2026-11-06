import math

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import MementoManager
from app.exceptions import CalculatorError
from app.history import History, AutoSaveObserver, LoggingObserver
from app.logger import configure_logging 
from app.input_validators import validate_number, validate_operation
import logging
from colorama import Fore, Style, init

init(autoreset=True)

class Calculator:
    """Facade that provides a simple interface to the calculator system."""

    def __init__(self):
        self.config = CalculatorConfig()
        self.logger = configure_logging(self.config.log_file)
        self.history = History(self.config.max_history_size)
        self.memento_manager = MementoManager()
        self.history.add_observer(
            LoggingObserver(self.logger)
        )

        if self.config.auto_save:
            self.history.add_observer(
                AutoSaveObserver(self.config.history_file)
            )

        if self.config.history_file.exists():
            try:
                self.history.load_from_csv(self.config.history_file)
            except CalculatorError as exc:
                self.logger.error(
                    "Unable to restore calculation history: %s", exc
                )
                print(
                    Fore.YELLOW
                    + f"Warning: Saved history could not be loaded: {exc}"
                    + Style.RESET_ALL
                )

    def calculate(self, operation, a, b):
        """Validate input, perform a calculation, and store it."""
        try:
            operation = validate_operation(operation)
            a = validate_number(a)
            b = validate_number(b)
        except (CalculatorError, ValueError) as exc:
            self.logger.warning(
                "Invalid calculation input: %s",
                exc
            )
            raise

        # LBYL: check values before performing the calculation.
        if abs(a) > self.config.max_input_value:
            self.logger.warning(
                "First number exceeds maximum input value: %s", a
            )
            raise ValueError("First number exceeds maximum input value.")
            
        if abs(b) > self.config.max_input_value:
            self.logger.warning(
                "Second number exceeds maximum input value: %s", b
            )
            raise ValueError("Second number exceeds maximum input value.")

        calculation = Calculation(operation, a, b)
        
        try:
            result = calculation.perform()
            
            if isinstance(result, complex) or not math.isfinite(result):
                raise ValueError(
                    "Calculation must produce a finite real number."
                )
        
        except Exception:
            self.logger.exception(
                "Calculation failed: %s(%s, %s)",
                operation, a, b
            )
            raise

        self.logger.info(
            "Calculation completed: %s(%s, %s) = %s",
            operation, a, b, result
        )
        
        self.memento_manager.save_state(
            self.history.get_history()
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
        """Undo the last history change and notify observers."""
        current = self.history.get_history()
        restored = self.memento_manager.undo(current)

        if not restored.equals(current):
            self.history.data = restored
            self.history.notify_observers()

    def redo(self):
        """Redo the last undone history change and notify observers."""
        current = self.history.get_history()
        restored = self.memento_manager.redo(current)

        if not restored.equals(current):
            self.history.data = restored
            self.history.notify_observers()

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
        print("  modulus, int_divide, percent, abs_diff")
        print("Format: operation number1 number2")
        print("Example: add 5 3")
        print("Example: modulus 10 3")
        print("Commands:")
        print("  help, history, clear, undo, redo, save, load, exit")

    def start(self):
        """Start the calculator REPL."""
        print(Fore.CYAN + "Welcome to the Advanced Calculator!" + Style.RESET_ALL)
        print("Type 'help' for instructions or 'exit' to quit.")

        while True:
            try:
                command = input("Enter command: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if command == "exit":
                print("Goodbye!")
                break

            if command == "help":
                self.display_help()
                continue

            try:
                if command == "history":
                    print(self.show_history().to_string(index=False))
                    continue
                if command == "clear":
                    self.clear_history()
                    print(Fore.GREEN + "History cleared." + Style.RESET_ALL)
                    continue
                if command == "undo":
                    self.undo()
                    print(Fore.GREEN + "Undo complete." + Style.RESET_ALL)
                    continue
                if command == "redo":
                    self.redo()
                    print(Fore.GREEN + "Redo complete." + Style.RESET_ALL)
                    continue
            except (CalculatorError, ValueError, OSError) as exc:
                self.logger.error("History command failed: %s", exc)
                print(Fore.RED + f"Error: {exc}" + Style.RESET_ALL)
                continue

            try:
                if command == "save":
                    self.save()
                    print(Fore.GREEN + "History saved." + Style.RESET_ALL)
                    continue

                if command == "load":
                    self.load()
                    print(Fore.GREEN + "History loaded." + Style.RESET_ALL)
                    continue

                parts = command.split()

                if len(parts) != 3:
                    raise ValueError(
                        "Enter an operation followed by two numbers."
                    )

                operation, a, b = parts
                result = self.calculate(operation, a, b)
                print(Fore.GREEN + f"Result: {result}" + Style.RESET_ALL)

            # EAFP: attempt the operation and handle errors if they occur.
            except (CalculatorError, ValueError, ZeroDivisionError, OSError) as exc:
                print(Fore.RED + f"Error: {exc}" + Style.RESET_ALL)