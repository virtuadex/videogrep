"""
Interactive mode for VoxGrep CLI.

This module provides the main interactive wizard for configuring
and executing VoxGrep tasks through a menu-driven interface.

The main entry point is `interactive_mode()` which delegates to the
InteractiveWizard state machine for cleaner flow control.
"""

from argparse import Namespace
from typing import Any, Optional

import questionary

from .ui import console, print_session_summary
from .io import CLIContext
from .config import SessionConfig

from .workflows import (
    select_input_files, check_transcripts, configure_transcription,
    settings_menu, post_export_menu, search_settings_menu,
    get_output_filename, manage_files_menu
)
from .commands import run_voxgrep_search, execute_args, run_transcription_whisper
from .ngrams import interactive_ngrams_workflow
from ..utils.config import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_DEVICE,
    DEFAULT_SEARCH_TYPE,
    DEFAULT_IGNORED_WORDS
)
from ..utils.prefs import load_prefs, save_prefs


def create_default_args(input_files: list[str], prefs: dict[str, Any]) -> Namespace:
    """
    Create a Namespace with default arguments.

    Args:
        input_files: List of input file paths
        prefs: Preferences dictionary

    Returns:
        Namespace with default values

    Note:
        This function is kept for backward compatibility.
        New code should use SessionConfig.from_prefs() instead.
    """
    # Use SessionConfig for cleaner creation, then convert to Namespace
    session = SessionConfig.from_prefs(prefs, input_files)
    return session.to_namespace()


def get_default_output_name(search_terms: list[str] | None) -> str:
    """Get a safe default output name from search terms."""
    default_out = "supercut"
    if search_terms:
        safe_term = "".join([
            c if c.isalnum() or c in (' ', '-', '_') else ''
            for c in search_terms[0]
        ]).strip().replace(' ', '_')
        if safe_term:
            default_out = safe_term
    return default_out


def handle_search_workflow(args: Namespace) -> bool:
    """
    Handle the search workflow including preview, export, and settings.

    Args:
        args: Namespace with search configuration

    Returns:
        True to continue main loop, False to exit
    """
    # Get search terms
    search_input = questionary.text("Enter search terms (comma separated):").ask()
    if not search_input:
        return True

    args.search = [s.strip() for s in search_input.split(',') if s.strip()]

    # Select search type
    args.searchtype = questionary.select(
        "Search Type",
        choices=["sentence", "fragment", "mash", "semantic"],
        default=args.searchtype
    ).ask()

    # Search workflow loop
    while True:
        default_out = get_default_output_name(args.search)

        # Show menu
        action = questionary.select(
            "Next Step:",
            choices=[
                questionary.Choice("Preview Results (MPV)", value="preview"),
                questionary.Choice(f"Export Supercut (to {default_out}.mp4...)", value="export"),
                questionary.Separator(),
                questionary.Choice(f"Settings (Padding: {args.padding or 0}s, Max: {args.maxclips or 'All'})", value="settings"),
                questionary.Choice("Start Over (New Search)", value="cancel")
            ],
            default="preview"
        ).ask()

        if action == "cancel":
            return True

        if action == "preview":
            console.print("\n[bold yellow]Generating Preview...[/bold yellow]")
            result = run_voxgrep_search(
                files=args.inputfile,
                query=args.search,
                search_type=args.searchtype,
                output=args.outputfile,
                maxclips=args.maxclips,
                padding=args.padding,
                demo=False,
                random_order=args.randomize,
                resync=args.sync,
                export_clips=args.export_clips,
                write_vtt=args.write_vtt,
                preview=True,
                exact_match=args.exact_match,
                burn_in_subtitles=args.burn_in_subtitles
            )

            if isinstance(result, dict):
                print_session_summary(result)

            continue

        if action == "settings":
            search_settings_menu(args)
            continue

        if action == "export":
            args.preview = False
            args.demo = False
            args.outputfile = get_output_filename(args.search, default_out)

            # Run export with progress
            result = run_voxgrep_search(
                files=args.inputfile,
                query=args.search,
                search_type=args.searchtype,
                output=args.outputfile,
                maxclips=args.maxclips,
                padding=args.padding,
                demo=False,
                random_order=args.randomize,
                resync=args.sync,
                export_clips=args.export_clips,
                write_vtt=args.write_vtt,
                preview=False,
                exact_match=args.exact_match,
                burn_in_subtitles=args.burn_in_subtitles
            )

            if isinstance(result, dict) and result.get("success"):
                print_session_summary(result)

            # Post-export menu
            if result:
                while True:
                    post_action = post_export_menu(args.outputfile)

                    if post_action == "edit":
                        break  # Back to search workflow loop
                    elif post_action in ("new", "menu"):
                        return True  # Back to main menu

                if post_action == "edit":
                    continue

            return True

    return True


def interactive_mode(ctx: Optional[CLIContext] = None) -> None:
    """
    Run an interactive wizard to gather arguments and execute tasks.

    This function delegates to the InteractiveWizard state machine for
    cleaner flow control and better testability.

    Args:
        ctx: Optional CLI context for dependency injection. If None,
             uses default production implementations.
    """
    from .wizard import InteractiveWizard

    wizard = InteractiveWizard(ctx)
    wizard.run()
