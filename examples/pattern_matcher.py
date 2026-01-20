import argparse
import voxgrep
from voxgrep import transcribe
from spacy.matcher import Matcher

try:
    from .utils import load_spacy_model
except (ImportError, ValueError):
    from utils import load_spacy_model

"""
Uses rule-based matching from spacy to make supercuts:
...
"""

def main():
    parser = argparse.ArgumentParser(description="Uses rule-based matching from spacy to make supercuts.")
    parser.add_argument("videos", nargs="+", help="The videos we are working with")
    parser.add_argument("--lang", choices=["en", "pt"], default="en", help="Language: en or pt. Default: en.")
    
    args = parser.parse_args()

    nlp = load_spacy_model(args.lang)

    # grabs all instances of adjectives followed by nouns
    patterns = [[{"POS": "ADJ"}, {"POS": "NOUN"}]]

    matcher = Matcher(nlp.vocab)
    matcher.add("Patterns", patterns)


    searches = []

    for video in args.videos:
        # ensure transcript exists
        if not voxgrep.find_transcript(video):
            print(f"Transcript not found for {video}. Transcribing with Whisper...")
            transcribe.transcribe(video, method="whisper")

        transcript = voxgrep.parse_transcript(video)
        if not transcript:
            continue

        for sentence in transcript:
            doc = nlp(sentence["content"])
            matches = matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]  # The matched span
                searches.append(span.text)

    if searches:
        voxgrep.voxgrep(
            args.videos, searches, search_type="fragment", output="pattern_matcher.mp4"
        )
    else:
        print("No pattern matches found.")

if __name__ == "__main__":
    main()
