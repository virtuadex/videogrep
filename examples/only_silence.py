import sys
import videogrep
from videogrep import parse_transcript, create_supercut, transcribe

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
    if not videogrep.find_transcript(filename):
        print(f"Transcript not found for {filename}. Transcribing with Whisper...")
        transcribe.transcribe(filename, method="whisper")

    timestamps = parse_transcript(filename)

    # this uses the words, if available
    words = []
    for sentence in timestamps:
        if 'words' in sentence:
            words += sentence['words']

    if not words:
        print(f"Warning: No word-level timestamps found for {filename}. Using sentences instead.")
        for sentence1, sentence2 in zip(timestamps[:-2], timestamps[1:]):
            start = sentence1['end']
            end = sentence2['start'] - adjuster
            duration = end - start
            if duration > min_duration and duration < max_duration:
               silences.append({'start': start, 'end': end, 'file': filename})
    else:
        for word1, word2 in zip(words[:-2], words[1:]):
            start = word1['end']
            end = word2['start'] - adjuster
            duration = end - start
            if duration > min_duration and duration < max_duration:
                silences.append({'start': start, 'end': end, 'file': filename})

if silences:
    create_supercut(silences, 'silences.mp4')
else:
    print("No silences found matching the criteria.")
