import sys
import voxgrep
from voxgrep import parse_transcript, create_supercut, transcribe

try:
    from .utils import calculate_silences
except (ImportError, ValueError):
    from utils import calculate_silences

# the min and max duration of silences to extract
min_duration = 0.5
max_duration = 1.0

# value to to trim off the end of each clip
adjuster = 0.1


filenames = sys.argv[1:]

if not filenames:
    print("Usage: python only_silence.py <video_file(s)>")
    sys.exit(1)

silences = []
for filename in filenames:
    # ensure transcript exists
    if not voxgrep.find_transcript(filename):
        print(f"Transcript not found for {filename}. Transcribing with Whisper...")
        transcribe.transcribe(filename, method="whisper")

    timestamps = parse_transcript(filename)
    if not timestamps:
        continue

    silences += calculate_silences(
        timestamps, filename, min_duration, max_duration, adjuster
    )

if silences:
    create_supercut(silences, 'silences.mp4')
else:
    print("No silences found matching the criteria.")
