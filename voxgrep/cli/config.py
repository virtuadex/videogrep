"""
Typed configuration dataclasses for VoxGrep CLI.

This module provides strongly-typed configuration objects that replace
loose Namespace/dict passing throughout the CLI code, improving type
safety, IDE support, and testability.
"""

from argparse import Namespace
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from ..utils.config import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_DEVICE,
    DEFAULT_COMPUTE_TYPE,
    DEFAULT_SEARCH_TYPE,
    DEFAULT_IGNORED_WORDS,
)


@dataclass
class TranscriptionConfig:
    """Configuration for Whisper transcription."""

    model: str = DEFAULT_WHISPER_MODEL
    device: str = DEFAULT_DEVICE
    compute_type: str = DEFAULT_COMPUTE_TYPE
    language: Optional[str] = None
    prompt: Optional[str] = None
    beam_size: int = 5
    best_of: int = 5
    vad_filter: bool = True
    normalize_audio: bool = False
    translate: bool = False

    @classmethod
    def from_namespace(cls, args: Namespace) -> "TranscriptionConfig":
        """Create TranscriptionConfig from argparse Namespace."""
        return cls(
            model=getattr(args, 'model', DEFAULT_WHISPER_MODEL),
            device=getattr(args, 'device', DEFAULT_DEVICE),
            compute_type=getattr(args, 'compute_type', DEFAULT_COMPUTE_TYPE),
            language=getattr(args, 'language', None),
            prompt=getattr(args, 'prompt', None),
            beam_size=getattr(args, 'beam_size', 5),
            best_of=getattr(args, 'best_of', 5),
            vad_filter=getattr(args, 'vad_filter', True),
            normalize_audio=getattr(args, 'normalize_audio', False),
            translate=getattr(args, 'translate', False),
        )

    @classmethod
    def from_prefs(cls, prefs: dict[str, Any]) -> "TranscriptionConfig":
        """Create TranscriptionConfig from preferences dictionary."""
        return cls(
            model=prefs.get('whisper_model', DEFAULT_WHISPER_MODEL),
            device=prefs.get('device', DEFAULT_DEVICE),
            compute_type=prefs.get('compute_type', DEFAULT_COMPUTE_TYPE),
            language=None,
            prompt=None,
            beam_size=prefs.get('beam_size', 5),
            best_of=prefs.get('best_of', 5),
            vad_filter=prefs.get('vad_filter', True),
            normalize_audio=prefs.get('normalize_audio', False),
            translate=False,
        )

    def to_namespace_update(self, args: Namespace) -> None:
        """Update an existing Namespace with this config's values."""
        args.model = self.model
        args.device = self.device
        args.compute_type = self.compute_type
        args.language = self.language
        args.prompt = self.prompt
        args.beam_size = self.beam_size
        args.best_of = self.best_of
        args.vad_filter = self.vad_filter
        args.normalize_audio = self.normalize_audio
        args.translate = self.translate

    def to_prefs_update(self) -> dict[str, Any]:
        """Return dict of preference keys to update."""
        return {
            'whisper_model': self.model,
            'device': self.device,
            'compute_type': self.compute_type,
            'beam_size': self.beam_size,
            'best_of': self.best_of,
            'vad_filter': self.vad_filter,
            'normalize_audio': self.normalize_audio,
        }


@dataclass
class SearchConfig:
    """Configuration for search operations."""

    query: list[str] = field(default_factory=list)
    search_type: str = DEFAULT_SEARCH_TYPE
    maxclips: int = 0
    padding: Optional[float] = None
    randomize: bool = False
    exact_match: bool = False
    resync: float = 0
    ignored_words: list[str] = field(default_factory=lambda: DEFAULT_IGNORED_WORDS.copy())
    use_ignored_words: bool = True

    @classmethod
    def from_namespace(cls, args: Namespace) -> "SearchConfig":
        """Create SearchConfig from argparse Namespace."""
        return cls(
            query=getattr(args, 'search', None) or [],
            search_type=getattr(args, 'searchtype', DEFAULT_SEARCH_TYPE),
            maxclips=getattr(args, 'maxclips', 0),
            padding=getattr(args, 'padding', None),
            randomize=getattr(args, 'randomize', False),
            exact_match=getattr(args, 'exact_match', False),
            resync=getattr(args, 'sync', 0),
            ignored_words=getattr(args, 'ignored_words', DEFAULT_IGNORED_WORDS.copy()),
            use_ignored_words=getattr(args, 'use_ignored_words', True),
        )

    @classmethod
    def from_prefs(cls, prefs: dict[str, Any]) -> "SearchConfig":
        """Create SearchConfig from preferences dictionary."""
        return cls(
            query=[],
            search_type=prefs.get('search_type', DEFAULT_SEARCH_TYPE),
            maxclips=0,
            padding=None,
            randomize=False,
            exact_match=False,
            resync=0,
            ignored_words=prefs.get('ignored_words', DEFAULT_IGNORED_WORDS.copy()),
            use_ignored_words=prefs.get('use_ignored_words', True),
        )

    def to_namespace_update(self, args: Namespace) -> None:
        """Update an existing Namespace with this config's values."""
        args.search = self.query
        args.searchtype = self.search_type
        args.maxclips = self.maxclips
        args.padding = self.padding
        args.randomize = self.randomize
        args.exact_match = self.exact_match
        args.sync = self.resync
        args.ignored_words = self.ignored_words
        args.use_ignored_words = self.use_ignored_words

    def to_prefs_update(self) -> dict[str, Any]:
        """Return dict of preference keys to update."""
        return {
            'search_type': self.search_type,
            'ignored_words': self.ignored_words,
            'use_ignored_words': self.use_ignored_words,
        }


@dataclass
class ExportConfig:
    """Configuration for export operations."""

    output: str = "supercut.mp4"
    preview: bool = False
    demo: bool = False
    export_clips: bool = False
    write_vtt: bool = False
    burn_in_subtitles: bool = False

    @classmethod
    def from_namespace(cls, args: Namespace) -> "ExportConfig":
        """Create ExportConfig from argparse Namespace."""
        return cls(
            output=getattr(args, 'outputfile', "supercut.mp4"),
            preview=getattr(args, 'preview', False),
            demo=getattr(args, 'demo', False),
            export_clips=getattr(args, 'export_clips', False),
            write_vtt=getattr(args, 'write_vtt', False),
            burn_in_subtitles=getattr(args, 'burn_in_subtitles', False),
        )

    @classmethod
    def from_prefs(cls, prefs: dict[str, Any]) -> "ExportConfig":
        """Create ExportConfig from preferences dictionary."""
        return cls(
            output="supercut.mp4",
            preview=prefs.get('preview', False),
            demo=prefs.get('demo', False),
            export_clips=False,
            write_vtt=False,
            burn_in_subtitles=prefs.get('burn_in_subtitles', False),
        )

    def to_namespace_update(self, args: Namespace) -> None:
        """Update an existing Namespace with this config's values."""
        args.outputfile = self.output
        args.preview = self.preview
        args.demo = self.demo
        args.export_clips = self.export_clips
        args.write_vtt = self.write_vtt
        args.burn_in_subtitles = self.burn_in_subtitles

    def to_prefs_update(self) -> dict[str, Any]:
        """Return dict of preference keys to update."""
        return {
            'preview': self.preview,
            'demo': self.demo,
            'burn_in_subtitles': self.burn_in_subtitles,
        }


@dataclass
class SessionConfig:
    """
    Complete session configuration combining all aspects.

    This is the top-level configuration object that holds all settings
    for a VoxGrep interactive session.
    """

    input_files: list[str] = field(default_factory=list)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    transcribe: bool = False
    ngrams: int = 0

    @classmethod
    def from_namespace(cls, args: Namespace) -> "SessionConfig":
        """Create SessionConfig from argparse Namespace."""
        return cls(
            input_files=getattr(args, 'inputfile', None) or [],
            transcription=TranscriptionConfig.from_namespace(args),
            search=SearchConfig.from_namespace(args),
            export=ExportConfig.from_namespace(args),
            transcribe=getattr(args, 'transcribe', False),
            ngrams=getattr(args, 'ngrams', 0),
        )

    @classmethod
    def from_prefs(cls, prefs: dict[str, Any], input_files: Optional[list[str]] = None) -> "SessionConfig":
        """Create SessionConfig from preferences dictionary."""
        return cls(
            input_files=input_files or [],
            transcription=TranscriptionConfig.from_prefs(prefs),
            search=SearchConfig.from_prefs(prefs),
            export=ExportConfig.from_prefs(prefs),
            transcribe=False,
            ngrams=0,
        )

    def to_namespace(self) -> Namespace:
        """Convert to argparse Namespace for backward compatibility."""
        args = Namespace()
        args.inputfile = self.input_files
        args.transcribe = self.transcribe
        args.ngrams = self.ngrams

        self.transcription.to_namespace_update(args)
        self.search.to_namespace_update(args)
        self.export.to_namespace_update(args)

        return args

    def to_prefs_update(self) -> dict[str, Any]:
        """Return dict of all preference keys to update."""
        prefs = {}
        prefs.update(self.transcription.to_prefs_update())
        prefs.update(self.search.to_prefs_update())
        prefs.update(self.export.to_prefs_update())
        return prefs
