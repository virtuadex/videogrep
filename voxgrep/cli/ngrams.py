"""
Interactive n-gram analysis workflow for VoxGrep CLI.

This module handles the complex interactive workflow for n-gram
calculation, selection, filtering, and search operations.
"""

from argparse import Namespace
from typing import Optional

import questionary

from .ui import console, print_session_summary
from .io import CLIContext
from .config import SearchConfig, ExportConfig
from .action_loop import (
    ActionLoop, ActionLoopState, ActionResult, Action, separator,
    create_preview_handler, create_exit_handler, create_back_handler
)

from .workflows import get_output_filename, post_export_menu
from .commands import calculate_ngrams, run_voxgrep_search


def select_ngrams_single_mode(
    most_common: list[tuple[tuple, int]],
    selected_ngrams_set: set[str],
    ctx: Optional[CLIContext] = None,
) -> tuple[str | None, set[str], str | None]:
    """
    Single-select mode for n-gram selection.

    Args:
        most_common: List of (ngram, count) tuples
        selected_ngrams_set: Currently selected n-grams
        ctx: Optional CLI context for prompts

    Returns:
        Tuple of (action, updated_selection, word_to_ignore)
    """
    prompts = ctx.prompts if ctx else None
    con = ctx.console if ctx else console

    choices = []
    choices.append(questionary.Choice(
        "[+] Switch to Multi-Select Mode (Checkboxes)",
        value="__SWITCH_MULTI__"
    ))

    if selected_ngrams_set:
        choices.append(questionary.Choice(
            f"  [!] Use Current Selection ({len(selected_ngrams_set)} items)",
            value="__USE_EXISTING__"
        ))

    choices.append(questionary.Choice(
        "[X] Add Word to Ignored List (Filter Out)",
        value="__IGNORE_WORD__"
    ))

    choices.append(questionary.Separator())

    for ngram, count in most_common:
        val = " ".join(ngram)
        label = f"{val} ({count}x)"
        choices.append(questionary.Choice(label, value=val))

    choices.append(questionary.Separator())
    choices.append(questionary.Choice("  [Back to Main Menu]", value="__EXIT__"))

    con.print("\n[bold cyan]--- Select N-gram (Type to filter, Enter to select) ---[/bold cyan]")

    if prompts:
        selection = prompts.select("Select n-gram:", choices)
    else:
        selection = questionary.select(
            "Select n-gram:",
            choices=choices,
            style=questionary.Style([('highlighted', 'fg:cyan bold')]),
            use_indicator=True
        ).ask()

    if selection is None or selection == "__EXIT__":
        return "__EXIT__", selected_ngrams_set, None

    if selection == "__SWITCH_MULTI__":
        return "__SWITCH_MULTI__", selected_ngrams_set, None

    if selection == "__USE_EXISTING__":
        return "__DONE__", selected_ngrams_set, None

    if selection == "__IGNORE_WORD__":
        return "__IGNORE_WORD__", selected_ngrams_set, None

    # Immediate selection
    return "__DONE__", {selection}, None


def select_ngrams_multi_mode(
    most_common: list[tuple[tuple, int]],
    selected_ngrams_set: set[str],
    ctx: Optional[CLIContext] = None,
) -> tuple[str | None, set[str], str | None]:
    """
    Multi-select mode for n-gram selection.

    Args:
        most_common: List of (ngram, count) tuples
        selected_ngrams_set: Currently selected n-grams
        ctx: Optional CLI context for prompts

    Returns:
        Tuple of (action, updated_selection, word_to_ignore)
    """
    prompts = ctx.prompts if ctx else None
    con = ctx.console if ctx else console

    checkbox_choices = []

    for ngram, count in most_common:
        val = " ".join(ngram)
        label = f"{val} ({count}x)"
        is_checked = val in selected_ngrams_set
        checkbox_choices.append(questionary.Choice(label, value=val, checked=is_checked))

    checkbox_choices.append(questionary.Separator())
    checkbox_choices.append(questionary.Choice("  Done / Confirm Selection", value="__DONE__"))
    checkbox_choices.append(questionary.Choice("  [x] Switch back to Single Select", value="__SWITCH_SINGLE__"))

    con.print("\n[bold cyan]--- Multi-Select N-grams (Space to toggle, Enter to confirm) ---[/bold cyan]")

    if prompts:
        page_selection = prompts.checkbox("Select n-grams:", checkbox_choices)
    else:
        page_selection = questionary.checkbox(
            "Select n-grams:",
            choices=checkbox_choices,
            style=questionary.Style([('highlighted', 'fg:cyan bold')])
        ).ask()

    if page_selection is None:
        return "__EXIT__", selected_ngrams_set, None

    # Handle control options
    if "__SWITCH_SINGLE__" in page_selection:
        # Capture valid selections before switching
        for val in page_selection:
            if val and not val.startswith("__"):
                selected_ngrams_set.add(val)
        return "__SWITCH_SINGLE__", selected_ngrams_set, None

    # Extract valid selections
    new_set = set()
    for val in page_selection:
        if val and not val.startswith("__"):
            new_set.add(val)

    if not new_set and "__DONE__" not in page_selection:
        # User hit enter without selecting anything
        con.print("[yellow]No n-grams selected.[/yellow]")
        return "__CONTINUE__", selected_ngrams_set, None

    return "__DONE__", new_set, None


def ngram_selection_phase(
    most_common: list[tuple[tuple, int]],
    ctx: Optional[CLIContext] = None,
) -> list[str] | tuple[str, str] | None:
    """
    Handle the interactive n-gram selection phase.

    Args:
        most_common: List of (ngram, count) tuples
        ctx: Optional CLI context for prompts

    Returns:
        List of selected n-grams, tuple of ("__REFRESH__", word) if ignoring, or None if cancelled
    """
    prompts = ctx.prompts if ctx else None
    con = ctx.console if ctx else console

    if not most_common:
        con.print("[yellow]No n-grams found.[/yellow]")
        return None

    con.print("\n[green]Select n-gram to search (or switch to Multi-Select):[/green]")

    selected_ngrams_set: set[str] = set()
    mode = "single"

    while True:
        if mode == "single":
            action, selected_ngrams_set, word_to_ignore = select_ngrams_single_mode(
                most_common, selected_ngrams_set, ctx
            )
        else:
            action, selected_ngrams_set, word_to_ignore = select_ngrams_multi_mode(
                most_common, selected_ngrams_set, ctx
            )

        if action == "__EXIT__":
            return None
        elif action == "__SWITCH_MULTI__":
            mode = "multi"
        elif action == "__SWITCH_SINGLE__":
            mode = "single"
        elif action == "__IGNORE_WORD__":
            # Prompt user to type or select a word to ignore
            from ..utils.prefs import load_prefs, save_prefs

            # Build list of all unique words from n-grams
            all_words = set()
            for ngram, _ in most_common:
                for word in ngram:
                    all_words.add(word)

            if prompts:
                word_to_ignore = prompts.autocomplete(
                    "Enter word to add to ignored list:",
                    sorted(all_words)
                )
            else:
                word_to_ignore = questionary.autocomplete(
                    "Enter word to add to ignored list:",
                    choices=sorted(all_words),
                    style=questionary.Style([('highlighted', 'fg:cyan bold')])
                ).ask()

            if word_to_ignore:
                # Add to preferences
                prefs = load_prefs()
                ignored_words = prefs.get("ignored_words", [])
                if word_to_ignore.lower() not in [w.lower() for w in ignored_words]:
                    ignored_words.append(word_to_ignore.lower())
                    prefs["ignored_words"] = ignored_words
                    save_prefs(prefs)
                    con.print(f"[green]Added '{word_to_ignore}' to ignored words list.[/green]")
                    # Signal to refresh n-grams
                    return ("__REFRESH__", word_to_ignore)
                else:
                    con.print(f"[yellow]'{word_to_ignore}' is already in the ignored list.[/yellow]")
            continue
        elif action == "__DONE__":
            return list(selected_ngrams_set)
        elif action == "__CONTINUE__":
            continue


def ngram_action_phase(
    args: Namespace,
    selected_ngrams: list[str],
    ctx: Optional[CLIContext] = None,
) -> bool:
    """
    Handle the n-gram action phase (demo, preview, export) using ActionLoop.

    Args:
        args: Original arguments namespace
        selected_ngrams: List of selected n-grams
        ctx: Optional CLI context for dependency injection

    Returns:
        True to go back to selection, False to exit
    """
    # Use default context if not provided
    if ctx is None:
        ctx = CLIContext.default()

    # Create config objects from args
    search = SearchConfig(
        query=selected_ngrams,
        search_type="sentence",
        maxclips=0,
        padding=None,
        randomize=False,
        exact_match=getattr(args, 'exact_match', False),
        resync=0,
        ignored_words=getattr(args, 'ignored_words', []),
        use_ignored_words=getattr(args, 'use_ignored_words', True),
    )

    export = ExportConfig(
        output="ngram_supercut.mp4",
        preview=False,
        demo=False,
        export_clips=False,
        write_vtt=False,
        burn_in_subtitles=getattr(args, 'burn_in_subtitles', False),
    )

    # Show demo if requested
    show_demo = ctx.prompts.confirm("Show text results table (Demo Mode)?", default=True)
    if show_demo:
        result = run_voxgrep_search(
            files=args.inputfile,
            query=search.query,
            search_type=search.search_type,
            output=export.output,
            maxclips=search.maxclips,
            padding=search.padding,
            demo=True,
            random_order=search.randomize,
            resync=search.resync,
            export_clips=export.export_clips,
            write_vtt=export.write_vtt,
            preview=False,
            exact_match=search.exact_match,
            burn_in_subtitles=export.burn_in_subtitles
        )
        if isinstance(result, dict):
            print_session_summary(result)

    # Create action loop state
    state = ActionLoopState(
        search=search,
        export=export,
        input_files=args.inputfile,
        ctx=ctx,
    )

    # Define handlers
    def preview_handler(s: ActionLoopState) -> ActionResult:
        s.export.preview = True
        s.export.output = "preview_temp.mp4"
        result = s.run_search(preview=True)
        if isinstance(result, dict):
            print_session_summary(result)
        s.export.preview = False
        return ActionResult.CONTINUE

    def export_handler(s: ActionLoopState) -> ActionResult:
        default_out = get_output_filename(s.search.query, "ngram_supercut")
        s.export.output = get_output_filename(s.search.query, default_out)
        s.export.preview = False

        result = s.run_search()

        if isinstance(result, dict) and result.get("success"):
            print_session_summary(result)

        if result:
            post_act = post_export_menu(s.export.output)
            if post_act == "edit":
                return ActionResult.CONTINUE
            elif post_act in ("new", "main"):
                return ActionResult.EXIT
        else:
            s.ctx.console.print("[red]Export failed.[/red]")

        return ActionResult.CONTINUE

    def settings_handler(s: ActionLoopState) -> ActionResult:
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
        return ActionResult.CONTINUE

    # Build actions
    actions = [
        Action("Preview Results (MPV)", "preview", preview_handler),
        Action("Export Supercut", "export", export_handler),
        Action("Settings (Search Type, Padding, etc.)", "settings", settings_handler),
        Action("Edit Selection (Add/Remove N-grams)", "edit_selection", create_back_handler()),
        Action("Start Over (New Search)", "start_over", create_exit_handler()),
        Action("Cancel / Back", "cancel", create_exit_handler()),
    ]

    # Create and run action loop
    title = f"Action Menu ({' + '.join(selected_ngrams)})"
    loop = ActionLoop(title, actions, ctx, state)
    result = loop.run()

    # BACK means go back to selection, EXIT means exit entirely
    return result == ActionResult.BACK


def interactive_ngrams_workflow(
    args: Namespace,
    ctx: Optional[CLIContext] = None,
) -> None:
    """
    Main interactive workflow for n-gram analysis.

    Args:
        args: Arguments namespace with ngrams, inputfile, and filter settings
        ctx: Optional CLI context for dependency injection
    """
    con = ctx.console if ctx else console

    # Calculate n-grams
    most_common, filtered = calculate_ngrams(
        args.inputfile,
        args.ngrams,
        getattr(args, 'ignored_words', None),
        getattr(args, 'use_ignored_words', True)
    )

    if not most_common:
        return

    from .ui import print_ngrams_table
    print_ngrams_table(most_common, filtered, args.ngrams)

    # Selection and action loop
    while True:
        selected_ngrams = ngram_selection_phase(most_common, ctx)

        if not selected_ngrams:
            return  # User cancelled or no selection

        # Check if user wants to refresh (added word to ignore list)
        if isinstance(selected_ngrams, tuple) and selected_ngrams[0] == "__REFRESH__":
            con.print("\n[cyan]Recalculating n-grams with updated filter...[/cyan]")
            # Recalculate with updated ignored words
            most_common, filtered = calculate_ngrams(
                args.inputfile,
                args.ngrams,
                None,  # Load from prefs
                True   # Use filter
            )
            if not most_common:
                con.print("[yellow]No n-grams remaining after filtering.[/yellow]")
                return
            print_ngrams_table(most_common, filtered, args.ngrams)
            continue  # Go back to selection

        # Enter action phase
        back_to_selection = ngram_action_phase(args, selected_ngrams, ctx)

        if not back_to_selection:
            return  # User wants to exit or start over
