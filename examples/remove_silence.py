"""
This script will remove silences from videos, based on word-level timestamps
Adjust the min_duration variable to change the duration of silences to remove

to run: python3 remove_silences.py SOMEVIDEO.mp4
"""

import sys
import voxgrep
from voxgrep import parse_transcript, create_supercut_in_batches, transcribe

try:
    from .utils import merge_clips
except (ImportError, ValueError):
    from utils import merge_clips

# the min duration of silences to remove
min_duration = 1.0

filenames = sys.argv[1:]

if not filenames:
    print("Usage: python remove_silence.py <video_file(s)>")
    sys.exit(1)

clips = []

for filename in filenames:
    # ensure transcript exists
    if not voxgrep.find_transcript(filename):
        print(f"Transcript not found for {filename}. Transcribing with Whisper...")
        transcribe.transcribe(filename, method="whisper")

    timestamps = parse_transcript(filename)
    if not timestamps:
        continue

    items = []
    if "words" in timestamps[0]:
        for sentence in timestamps:
            items += sentence["words"]
    else:
        items = timestamps

    clips += merge_clips(items, filename, min_duration)


if clips:
    create_supercut_in_batches(clips, "no_silences.mp4")
else:
    print("No clips found to export.")
