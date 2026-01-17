__version__ = "2.3.1"

# Core modules
from . import vtt, srt, sphinx, fcpxml

# New infrastructure modules
from . import config, exceptions, utils

# Main voxgrep function and utilities
from .voxgrep import (
    voxgrep,
    remove_overlaps,
    pad_and_sync,
)

# Search engine
from .search_engine import (
    search,
    find_transcript,
    parse_transcript,
    get_ngrams,
    SUB_EXTS,  # Legacy compatibility
)

# Exporter
from .exporter import (
    create_supercut,
    create_supercut_in_batches,
    export_individual_clips,
    export_m3u,
    export_mpv_edl,
    export_xml,
    cleanup_log_files,
    get_file_type,
    get_input_type,
    plan_no_action,
    plan_video_output,
    plan_audio_output,
    BATCH_SIZE,  # Legacy compatibility
)

# Expose commonly used items from new modules
from .config import (
    SUBTITLE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS,
    MEDIA_EXTENSIONS,
)

from .exceptions import (
    VoxGrepError,
    TranscriptNotFoundError,
    SearchError,
    NoResultsFoundError,
)

from .utils import (
    is_video_file,
    is_audio_file,
    is_media_file,
    validate_media_file,
)

