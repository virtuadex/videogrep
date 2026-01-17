import random
import subprocess
import os
from typing import List, Union, Optional

from . import search_engine as search_module
from . import exporter
from . import vtt
from .config import DEFAULT_PADDING, BATCH_SIZE
from .utils import setup_logger, ensure_list, ensure_directory_exists

logger = setup_logger(__name__)


def remove_overlaps(segments: List[dict]) -> List[dict]:
    """
    Removes any time overlaps from clips, merging them into single segments.
    """
    if not segments:
        return []

    # Sort by start time
    segments = sorted(segments, key=lambda k: k["start"])
    
    out = [segments[0]]
    for segment in segments[1:]:
        # Only merge if it's the same file
        if segment["file"] == out[-1]["file"] and out[-1]["end"] >= segment["start"]:
            out[-1]["end"] = max(out[-1]["end"], segment["end"])
        else:
            out.append(segment)

    return out


def pad_and_sync(
    segments: List[dict], padding: float = 0, resync: float = 0
) -> List[dict]:
    """
    Adds padding and resyncs timestamps.
    """
    if not segments:
        return []

    processed = []
    for s in segments:
        new_segment = s.copy()
        if padding != 0:
            new_segment["start"] -= padding
            new_segment["end"] += padding
        if resync != 0:
            new_segment["start"] += resync
            new_segment["end"] += resync

        # Ensure bounds
        new_segment["start"] = max(0, new_segment["start"])
        new_segment["end"] = max(0, new_segment["end"])
        
        processed.append(new_segment)

    # Merge overlaps that were created by padding
    return remove_overlaps(processed)


def voxgrep(
    files: Union[List[str], str],
    query: Union[List[str], str],
    search_type: str = "sentence",
    output: str = "supercut.mp4",
    resync: float = 0,
    padding: Optional[float] = None,
    maxclips: int = 0,
    export_clips: bool = False,
    random_order: bool = False,
    demo: bool = False,
    write_vtt: bool = False,
    preview: bool = False,
) -> bool:
    """
    Main entry point for creating a supercut based on a search query.
    """
    files = ensure_list(files)
    query = ensure_list(query)

    # Perform search
    segments = search_module.search(files, query, search_type)

    if not segments:
        query_str = " ".join(query) if isinstance(query, list) else query
        logger.warning(f"No results found for: {query_str}")
        return False

    # Handle default padding
    if padding is None:
        if search_type in ["fragment", "mash"]:
            padding = DEFAULT_PADDING
        else:
            padding = 0

    # Apply padding and handle overlaps
    segments = pad_and_sync(segments, padding=padding, resync=resync)

    # Random order
    if random_order:
        random.shuffle(segments)

    # Limit clips
    if maxclips > 0:
        segments = segments[:maxclips]

    # Mode: Demo (dry run)
    if demo:
        for s in segments:
            print(f"{s['file']} | {s['start']:.2f} - {s['end']:.2f} | {s['content']}")
        return True

    # Mode: Preview (MPV)
    if preview:
        lines = [f"{os.path.abspath(s['file'])},{s['start']},{s['end']-s['start']}" for s in segments]
        edl = "edl://" + ";".join(lines)
        try:
            subprocess.run(["mpv", edl], check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Could not launch mpv for preview. Is it installed?")
        return True

    # Ensure output directory exists
    ensure_directory_exists(os.path.dirname(os.path.abspath(output)))

    # Export Logic
    if export_clips:
        exporter.export_individual_clips(segments, output)
    elif output.endswith(".m3u"):
        exporter.export_m3u(segments, output)
    elif output.endswith(".mpv.edl"):
        exporter.export_mpv_edl(segments, output)
    elif output.endswith(".xml"):
        exporter.export_xml(segments, output)
    else:
        # Create full supercut
        if len(segments) > BATCH_SIZE:
            exporter.create_supercut_in_batches(segments, output)
        else:
            exporter.create_supercut(segments, output)

    # Write WebVTT if requested
    if write_vtt:
        vtt_path = os.path.splitext(output)[0] + ".vtt"
        vtt.render(segments, vtt_path)
        logger.info(f"Subtitle file written to: {vtt_path}")
    
    return True
