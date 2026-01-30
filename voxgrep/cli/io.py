"""
Dependency injection layer for VoxGrep CLI I/O operations.

This module provides abstract interfaces for user prompts and console output,
enabling the CLI to be tested without requiring actual user interaction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Generic, Sequence

import questionary
from rich.console import Console

from ..utils.prefs import load_prefs, save_prefs

T = TypeVar('T')


class PromptProvider(ABC):
    """
    Abstract interface for user prompts.

    Implementations can use questionary (production) or return
    predetermined values (testing).
    """

    @abstractmethod
    def select(
        self,
        message: str,
        choices: Sequence[Any],
        default: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Prompt user to select one option from choices.

        Args:
            message: The prompt message to display
            choices: List of choices (strings or questionary.Choice objects)
            default: Default selection

        Returns:
            Selected value, or None if cancelled
        """
        ...

    @abstractmethod
    def checkbox(
        self,
        message: str,
        choices: Sequence[Any]
    ) -> Optional[list[Any]]:
        """
        Prompt user to select multiple options.

        Args:
            message: The prompt message to display
            choices: List of choices

        Returns:
            List of selected values, or None if cancelled
        """
        ...

    @abstractmethod
    def text(
        self,
        message: str,
        default: str = "",
        validate: Optional[Callable[[str], bool | str]] = None
    ) -> Optional[str]:
        """
        Prompt user for text input.

        Args:
            message: The prompt message to display
            default: Default text value
            validate: Optional validation function

        Returns:
            User input string, or None if cancelled
        """
        ...

    @abstractmethod
    def confirm(
        self,
        message: str,
        default: bool = False
    ) -> Optional[bool]:
        """
        Prompt user for yes/no confirmation.

        Args:
            message: The prompt message to display
            default: Default value if user presses enter

        Returns:
            True/False, or None if cancelled
        """
        ...

    @abstractmethod
    def autocomplete(
        self,
        message: str,
        choices: Sequence[str],
        default: str = ""
    ) -> Optional[str]:
        """
        Prompt user for text with autocomplete suggestions.

        Args:
            message: The prompt message to display
            choices: List of autocomplete suggestions
            default: Default text value

        Returns:
            User input string, or None if cancelled
        """
        ...


class ConsoleProvider(ABC):
    """
    Abstract interface for console output.

    Implementations can use Rich (production) or capture output (testing).
    """

    @abstractmethod
    def print(self, message: str, **kwargs: Any) -> None:
        """Print a message to the console."""
        ...

    @abstractmethod
    def status(self, message: str) -> Any:
        """
        Create a status spinner context manager.

        Args:
            message: Status message to display

        Returns:
            Context manager that shows a spinner while active
        """
        ...

    @abstractmethod
    def rule(self, title: str = "", **kwargs: Any) -> None:
        """Print a horizontal rule/divider."""
        ...


class QuestionaryPrompts(PromptProvider):
    """Production implementation using questionary."""

    def __init__(self, style: Optional[questionary.Style] = None):
        self._style = style or questionary.Style([
            ('highlighted', 'fg:cyan bold')
        ])

    def select(
        self,
        message: str,
        choices: Sequence[Any],
        default: Optional[Any] = None
    ) -> Optional[Any]:
        return questionary.select(
            message,
            choices=list(choices),
            default=default,
            style=self._style
        ).ask()

    def checkbox(
        self,
        message: str,
        choices: Sequence[Any]
    ) -> Optional[list[Any]]:
        return questionary.checkbox(
            message,
            choices=list(choices),
            style=self._style
        ).ask()

    def text(
        self,
        message: str,
        default: str = "",
        validate: Optional[Callable[[str], bool | str]] = None
    ) -> Optional[str]:
        return questionary.text(
            message,
            default=default,
            validate=validate
        ).ask()

    def confirm(
        self,
        message: str,
        default: bool = False
    ) -> Optional[bool]:
        return questionary.confirm(
            message,
            default=default
        ).ask()

    def autocomplete(
        self,
        message: str,
        choices: Sequence[str],
        default: str = ""
    ) -> Optional[str]:
        return questionary.autocomplete(
            message,
            choices=list(choices),
            default=default,
            style=self._style
        ).ask()


class RichConsole(ConsoleProvider):
    """Production implementation using Rich console."""

    def __init__(self, console: Optional[Console] = None):
        self._console = console

    @property
    def console(self) -> Console:
        """Lazy-load console to avoid import issues."""
        if self._console is None:
            from .ui import console as default_console
            self._console = default_console
        return self._console

    def print(self, message: str, **kwargs: Any) -> None:
        self.console.print(message, **kwargs)

    def status(self, message: str) -> Any:
        return self.console.status(message)

    def rule(self, title: str = "", **kwargs: Any) -> None:
        self.console.rule(title, **kwargs)


class MockPrompts(PromptProvider):
    """
    Testing implementation that returns predetermined values.

    Use this for unit tests to avoid actual user interaction.
    """

    def __init__(self, responses: Optional[list[Any]] = None):
        """
        Initialize with a list of responses to return in order.

        Args:
            responses: List of values to return for each prompt call
        """
        self._responses = list(responses) if responses else []
        self._call_history: list[dict[str, Any]] = []

    def _next_response(self, call_info: dict[str, Any]) -> Any:
        """Record the call and return the next response."""
        self._call_history.append(call_info)
        if self._responses:
            return self._responses.pop(0)
        return None

    @property
    def call_history(self) -> list[dict[str, Any]]:
        """Access the history of all prompt calls made."""
        return self._call_history

    def select(
        self,
        message: str,
        choices: Sequence[Any],
        default: Optional[Any] = None
    ) -> Optional[Any]:
        return self._next_response({
            'type': 'select',
            'message': message,
            'choices': list(choices),
            'default': default
        })

    def checkbox(
        self,
        message: str,
        choices: Sequence[Any]
    ) -> Optional[list[Any]]:
        return self._next_response({
            'type': 'checkbox',
            'message': message,
            'choices': list(choices)
        })

    def text(
        self,
        message: str,
        default: str = "",
        validate: Optional[Callable[[str], bool | str]] = None
    ) -> Optional[str]:
        return self._next_response({
            'type': 'text',
            'message': message,
            'default': default
        })

    def confirm(
        self,
        message: str,
        default: bool = False
    ) -> Optional[bool]:
        return self._next_response({
            'type': 'confirm',
            'message': message,
            'default': default
        })

    def autocomplete(
        self,
        message: str,
        choices: Sequence[str],
        default: str = ""
    ) -> Optional[str]:
        return self._next_response({
            'type': 'autocomplete',
            'message': message,
            'choices': list(choices),
            'default': default
        })


class MockConsole(ConsoleProvider):
    """
    Testing implementation that captures output.

    Use this for unit tests to verify console output without
    actually printing anything.
    """

    def __init__(self):
        self._output: list[str] = []
        self._status_messages: list[str] = []

    @property
    def output(self) -> list[str]:
        """Access all printed messages."""
        return self._output

    @property
    def status_messages(self) -> list[str]:
        """Access all status messages shown."""
        return self._status_messages

    def print(self, message: str, **kwargs: Any) -> None:
        self._output.append(message)

    def status(self, message: str) -> "MockStatusContext":
        self._status_messages.append(message)
        return MockStatusContext(self, message)

    def rule(self, title: str = "", **kwargs: Any) -> None:
        self._output.append(f"--- {title} ---" if title else "---")


class MockStatusContext:
    """Mock context manager for console.status()."""

    def __init__(self, console: MockConsole, message: str):
        self._console = console
        self._message = message

    def __enter__(self) -> "MockStatusContext":
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def update(self, message: str) -> None:
        self._console._status_messages.append(message)


@dataclass
class CLIContext:
    """
    Dependency injection container for CLI operations.

    This context holds all external dependencies that CLI functions need,
    allowing them to be easily swapped out for testing.
    """

    prompts: PromptProvider = field(default_factory=QuestionaryPrompts)
    console: ConsoleProvider = field(default_factory=RichConsole)
    prefs_loader: Callable[[], dict[str, Any]] = field(default=load_prefs)
    prefs_saver: Callable[[dict[str, Any]], None] = field(default=save_prefs)

    @classmethod
    def default(cls) -> "CLIContext":
        """Create a context with default production implementations."""
        return cls()

    @classmethod
    def for_testing(
        cls,
        responses: Optional[list[Any]] = None,
        prefs: Optional[dict[str, Any]] = None
    ) -> "CLIContext":
        """
        Create a context for testing with mock implementations.

        Args:
            responses: List of responses for MockPrompts to return
            prefs: Initial preferences dict for the mock prefs loader

        Returns:
            CLIContext configured for testing
        """
        test_prefs = prefs.copy() if prefs else {}

        def mock_loader() -> dict[str, Any]:
            return test_prefs.copy()

        def mock_saver(new_prefs: dict[str, Any]) -> None:
            test_prefs.update(new_prefs)

        return cls(
            prompts=MockPrompts(responses),
            console=MockConsole(),
            prefs_loader=mock_loader,
            prefs_saver=mock_saver,
        )
