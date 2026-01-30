"""
Reusable action loop pattern for VoxGrep CLI.

This module consolidates the duplicate action menu patterns found in
interactive.py and ngrams.py into a single, reusable component.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional, Protocol, Sequence

import questionary

from .config import SearchConfig, ExportConfig
from .io import CLIContext, PromptProvider, ConsoleProvider


class ActionResult(Enum):
    """Result of an action handler execution."""

    CONTINUE = auto()  # Continue the action loop
    BACK = auto()      # Go back to previous menu/phase
    EXIT = auto()      # Exit entirely


@dataclass
class Action:
    """
    A single action in an action loop menu.

    Attributes:
        label: Display text shown in the menu
        value: Internal value for this action
        handler: Function to execute when action is selected
        is_separator: If True, this is a visual separator, not a selectable action
    """

    label: str
    value: str
    handler: Optional[Callable[["ActionLoopState"], ActionResult]] = None
    is_separator: bool = False

    def to_choice(self) -> questionary.Choice | questionary.Separator:
        """Convert to questionary choice or separator."""
        if self.is_separator:
            return questionary.Separator()
        return questionary.Choice(self.label, value=self.value)


def separator() -> Action:
    """Create a separator action."""
    return Action(label="", value="__sep__", is_separator=True)


@dataclass
class ActionLoopState:
    """
    Mutable state passed to action handlers.

    This allows handlers to modify the search/export configuration
    and communicate with the action loop.
    """

    search: SearchConfig
    export: ExportConfig
    input_files: list[str]
    ctx: CLIContext

    # Mutable state that handlers can update
    result_data: dict[str, Any] = field(default_factory=dict)

    def run_search(self, preview: bool = False, demo: bool = False) -> Any:
        """
        Execute a search with current configuration.

        This is a convenience method that handlers can use to run
        the actual voxgrep search operation.
        """
        from .commands import run_voxgrep_search

        return run_voxgrep_search(
            files=self.input_files,
            query=self.search.query,
            search_type=self.search.search_type,
            output=self.export.output,
            maxclips=self.search.maxclips,
            padding=self.search.padding,
            demo=demo,
            random_order=self.search.randomize,
            resync=self.search.resync,
            export_clips=self.export.export_clips,
            write_vtt=self.export.write_vtt,
            preview=preview,
            exact_match=self.search.exact_match,
            burn_in_subtitles=self.export.burn_in_subtitles,
        )


class ActionLoop:
    """
    A reusable action menu loop.

    This class encapsulates the common pattern of:
    1. Display a menu of actions
    2. User selects an action
    3. Execute the action's handler
    4. Repeat or exit based on handler result
    """

    def __init__(
        self,
        title: str,
        actions: Sequence[Action],
        ctx: CLIContext,
        state: ActionLoopState,
        default_action: Optional[str] = None,
    ):
        """
        Initialize the action loop.

        Args:
            title: Title displayed above the menu
            actions: List of available actions
            ctx: CLI context for prompts and console
            state: Mutable state passed to handlers
            default_action: Default selection value
        """
        self.title = title
        self.actions = list(actions)
        self.ctx = ctx
        self.state = state
        self.default_action = default_action

        # Build lookup for action handlers
        self._handlers: dict[str, Callable[[ActionLoopState], ActionResult]] = {}
        for action in self.actions:
            if action.handler and not action.is_separator:
                self._handlers[action.value] = action.handler

    def _build_choices(self) -> list[Any]:
        """Build the list of questionary choices."""
        return [action.to_choice() for action in self.actions]

    def _get_menu_title(self) -> str:
        """Get the formatted menu title."""
        # Allow dynamic title that can include state info
        if callable(self.title):
            return self.title(self.state)
        return self.title

    def run(self) -> ActionResult:
        """
        Run the action loop until exit or back.

        Returns:
            ActionResult.EXIT if user exited
            ActionResult.BACK if user went back
        """
        while True:
            # Display title
            self.ctx.console.print(f"\n[bold cyan]--- {self._get_menu_title()} ---[/bold cyan]")

            # Show menu and get selection
            selection = self.ctx.prompts.select(
                "What would you like to do?",
                choices=self._build_choices(),
                default=self.default_action,
            )

            if selection is None:
                return ActionResult.EXIT

            # Find and execute handler
            handler = self._handlers.get(selection)
            if handler:
                result = handler(self.state)
                if result == ActionResult.EXIT:
                    return ActionResult.EXIT
                elif result == ActionResult.BACK:
                    return ActionResult.BACK
                # ActionResult.CONTINUE: loop continues

        return ActionResult.EXIT


# =============================================================================
# Standard Action Handlers
# =============================================================================

def create_preview_handler() -> Callable[[ActionLoopState], ActionResult]:
    """Create a standard preview action handler."""

    def handler(state: ActionLoopState) -> ActionResult:
        state.ctx.console.print("\n[bold yellow]Generating Preview...[/bold yellow]")
        result = state.run_search(preview=True)

        if isinstance(result, dict):
            from .ui import print_session_summary
            print_session_summary(result)

        return ActionResult.CONTINUE

    return handler


def create_demo_handler() -> Callable[[ActionLoopState], ActionResult]:
    """Create a standard demo (text results) action handler."""

    def handler(state: ActionLoopState) -> ActionResult:
        result = state.run_search(demo=True)

        if isinstance(result, dict):
            from .ui import print_session_summary
            print_session_summary(result)

        return ActionResult.CONTINUE

    return handler


def create_export_handler(
    get_filename: Callable[[ActionLoopState], str],
    post_export_menu: Optional[Callable[[str], str]] = None,
) -> Callable[[ActionLoopState], ActionResult]:
    """
    Create a standard export action handler.

    Args:
        get_filename: Function to get output filename from state
        post_export_menu: Optional function to show post-export menu
    """

    def handler(state: ActionLoopState) -> ActionResult:
        state.export.output = get_filename(state)
        state.export.preview = False
        state.export.demo = False

        result = state.run_search()

        if isinstance(result, dict) and result.get("success"):
            from .ui import print_session_summary
            print_session_summary(result)

        if result:
            if post_export_menu:
                post_action = post_export_menu(state.export.output)
                if post_action == "edit":
                    return ActionResult.CONTINUE
                elif post_action in ("new", "menu"):
                    return ActionResult.BACK
            else:
                return ActionResult.BACK

        return ActionResult.CONTINUE

    return handler


def create_settings_handler(
    settings_menu: Callable[[ActionLoopState], None]
) -> Callable[[ActionLoopState], ActionResult]:
    """
    Create a settings action handler.

    Args:
        settings_menu: Function to show settings configuration
    """

    def handler(state: ActionLoopState) -> ActionResult:
        settings_menu(state)
        return ActionResult.CONTINUE

    return handler


def create_back_handler() -> Callable[[ActionLoopState], ActionResult]:
    """Create a handler that returns BACK."""

    def handler(state: ActionLoopState) -> ActionResult:
        return ActionResult.BACK

    return handler


def create_exit_handler() -> Callable[[ActionLoopState], ActionResult]:
    """Create a handler that returns EXIT."""

    def handler(state: ActionLoopState) -> ActionResult:
        return ActionResult.EXIT

    return handler


# =============================================================================
# Pre-built Action Sets
# =============================================================================

def build_search_actions(
    state: ActionLoopState,
    get_default_output: Callable[[ActionLoopState], str],
) -> list[Action]:
    """
    Build standard search workflow actions.

    This creates the common action set used in both the main search workflow
    and the n-gram action phase.
    """
    from .workflows import post_export_menu, get_output_filename

    def settings_menu(s: ActionLoopState) -> None:
        """Configure search settings inline."""
        # Search type
        s.search.search_type = s.ctx.prompts.select(
            "Search Type",
            choices=["sentence", "fragment", "mash", "semantic"],
            default=s.search.search_type,
        ) or s.search.search_type

        # Padding
        padding_str = s.ctx.prompts.text(
            "Padding (seconds, e.g., 0.5):",
            default=str(s.search.padding) if s.search.padding else "",
        )
        s.search.padding = float(padding_str) if padding_str else None

        # Max clips
        maxclips_str = s.ctx.prompts.text(
            "Max clips (0 for all):",
            default=str(s.search.maxclips),
        )
        s.search.maxclips = int(maxclips_str) if maxclips_str else 0

        # Randomize
        s.search.randomize = s.ctx.prompts.confirm(
            "Randomize order?",
            default=s.search.randomize,
        ) or False

        # Exact match
        s.search.exact_match = s.ctx.prompts.confirm(
            "Exact Match (Whole Words Only)?",
            default=s.search.exact_match,
        ) or False

        # Burn-in subtitles
        s.export.burn_in_subtitles = s.ctx.prompts.confirm(
            "Burn-in Subtitles in output?",
            default=s.export.burn_in_subtitles,
        ) or False

        s.ctx.console.print(
            f"[green]Settings updated. Search Type: {s.search.search_type}, "
            f"Exact Match: {s.search.exact_match}, Burn-in: {s.export.burn_in_subtitles}[/green]"
        )

    def get_filename(s: ActionLoopState) -> str:
        default_out = get_default_output(s)
        return get_output_filename(s.search.query, default_out)

    default_out = get_default_output(state)
    padding_display = state.search.padding or 0
    max_display = state.search.maxclips or "All"

    return [
        Action(
            "Preview Results (MPV)",
            "preview",
            create_preview_handler(),
        ),
        Action(
            f"Export Supercut (to {default_out}.mp4...)",
            "export",
            create_export_handler(get_filename, post_export_menu),
        ),
        separator(),
        Action(
            f"Settings (Padding: {padding_display}s, Max: {max_display})",
            "settings",
            create_settings_handler(settings_menu),
        ),
        Action(
            "Start Over (New Search)",
            "cancel",
            create_back_handler(),
        ),
    ]


def build_ngram_actions(
    state: ActionLoopState,
    get_default_output: Callable[[ActionLoopState], str],
) -> list[Action]:
    """
    Build n-gram specific workflow actions.

    Similar to search actions but includes additional n-gram specific options.
    """
    from .workflows import post_export_menu, get_output_filename

    def settings_menu(s: ActionLoopState) -> None:
        """Configure search settings inline."""
        s.search.search_type = s.ctx.prompts.select(
            "Search Type",
            choices=["sentence", "fragment", "mash", "semantic"],
            default=s.search.search_type,
        ) or s.search.search_type

        padding_str = s.ctx.prompts.text(
            "Padding (seconds, e.g., 0.5):",
            default=str(s.search.padding) if s.search.padding else "",
        )
        s.search.padding = float(padding_str) if padding_str else None

        maxclips_str = s.ctx.prompts.text(
            "Max clips (0 for all):",
            default=str(s.search.maxclips),
        )
        s.search.maxclips = int(maxclips_str) if maxclips_str else 0

        s.search.randomize = s.ctx.prompts.confirm(
            "Randomize order?",
            default=s.search.randomize,
        ) or False

        s.search.exact_match = s.ctx.prompts.confirm(
            "Exact Match (Whole Words Only)?",
            default=s.search.exact_match,
        ) or False

        s.export.burn_in_subtitles = s.ctx.prompts.confirm(
            "Burn-in Subtitles in output?",
            default=s.export.burn_in_subtitles,
        ) or False

        s.ctx.console.print(
            f"[green]Settings updated. Search Type: {s.search.search_type}, "
            f"Exact Match: {s.search.exact_match}, Burn-in: {s.export.burn_in_subtitles}[/green]"
        )

    def get_filename(s: ActionLoopState) -> str:
        default_out = get_default_output(s)
        return get_output_filename(s.search.query, default_out)

    return [
        Action(
            "Preview Results (MPV)",
            "preview",
            create_preview_handler(),
        ),
        Action(
            "Export Supercut",
            "export",
            create_export_handler(get_filename, post_export_menu),
        ),
        Action(
            "Settings (Search Type, Padding, etc.)",
            "settings",
            create_settings_handler(settings_menu),
        ),
        Action(
            "Edit Selection (Add/Remove N-grams)",
            "edit_selection",
            create_back_handler(),  # Returns BACK to go to selection phase
        ),
        Action(
            "Start Over (New Search)",
            "start_over",
            create_exit_handler(),
        ),
        Action(
            "Cancel / Back",
            "cancel",
            create_exit_handler(),
        ),
    ]
