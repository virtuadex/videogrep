import sys
import os
import voxgrep
from voxgrep import transcribe
from collections import Counter
import random

try:
    from .utils import STOPWORDS
except (ImportError, ValueError):
    from utils import STOPWORDS

def auto_supercut(vidfile, total_words=3):
    """automatically creates a supercut from a video by selecting three random words"""

    # ensure transcript exists
    if not voxgrep.find_transcript(vidfile):
        print(f"Transcript not found for {vidfile}. Transcribing with Whisper...")
        transcribe.transcribe(vidfile, method="whisper")

    # grab all the words from the transcript
    unigrams = voxgrep.get_ngrams(vidfile)

    # remove stop words
    unigrams = [w for w in unigrams if w[0] not in STOPWORDS]

    # get the most common 10 words
    most_common = Counter(unigrams).most_common(10)

    # transform the list into just the words
    words = [w[0][0] for w in most_common]

    # randomize the list
    random.shuffle(words)

    # select the first N words
    words = words[0:total_words]

    # create a query
    query = "|".join(words)

    # create the video
    voxgrep.voxgrep(vidfile, query, search_type="fragment", output="auto_supercut.mp4")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_supercut.py <video_file>")
        sys.exit(1)
    vidfile = sys.argv[1]
    auto_supercut(vidfile)
