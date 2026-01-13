"""
This script will remove silences from videos, based on word-level timestamps
Adjust the min_duration variable to change the duration of silences to remove

to run: python3 remove_silences.py SOMEVIDEO.mp4
"""

import sys
import videogrep
from videogrep import parse_transcript, create_supercut_in_batches, transcribe

# the min duration of silences to remove
min_duration = 1.0

filenames = sys.argv[1:]

if not filenames:
    print("Usage: python remove_silence.py <video_file(s)>")
    sys.exit(1)

clips = []

for filename in filenames:
    # ensure transcript exists
    if not videogrep.find_transcript(filename):
        print(f"Transcript not found for {filename}. Transcribing with Whisper...")
        transcribe.transcribe(filename, method="whisper")

    timestamps = parse_transcript(filename)
    if not timestamps:
        continue

    if "words" in timestamps[0]:
        words = []
        for sentence in timestamps:
            words += sentence["words"]

        clip = {"start": words[0]["start"], "end": words[0]["end"], "file": filename}

        for word1, word2 in zip(words[:-2], words[1:]):
            silence_start = word1["end"]
            silence_end = word2["start"]
            duration = silence_end - silence_start

            if duration < min_duration:
                clip["end"] = word2["end"]

            elif duration >= min_duration:
                clip["end"] = word1["end"]
                clips.append(clip)
                clip = {"start": word2["start"], "end": word2["end"], "file": filename}
        
        # Add the last clip
        clips.append(clip)

    else:
        clip = {
            "start": timestamps[0]["start"],
            "end": timestamps[0]["end"],
            "file": filename,
        }
        for sentence1, sentence2 in zip(timestamps[:-2], timestamps[1:]):
            silence_start = sentence1["end"]
            silence_end = sentence2["start"]
            duration = silence_end - silence_start
            if duration < min_duration:
                clip["end"] = sentence2["end"]

            elif duration >= min_duration:
                clip["end"] = sentence1["end"]
                clips.append(clip)
                clip = {
                    "start": sentence2["start"],
                    "end": sentence2["end"],
                    "file": filename,
                }
        
        # Add the last clip
        clips.append(clip)


if clips:
    create_supercut_in_batches(clips, "no_silences.mp4")
else:
    print("No clips found to export.")
