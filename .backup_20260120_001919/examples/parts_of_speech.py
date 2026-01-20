import argparse
import voxgrep
from voxgrep import transcribe

try:
    from .utils import load_spacy_model
except (ImportError, ValueError):
    from utils import load_spacy_model

"""
Make a supercut of different types of words, for example, all nouns.
...
"""

def main():
    parser = argparse.ArgumentParser(description="Make a supercut of different types of words.")
    parser.add_argument("videos", nargs="+", help="The videos we are working with")
    parser.add_argument("--lang", choices=["en", "pt"], default="en", help="Language: en or pt. Default: en.")
    parser.add_argument("--pos", nargs="+", default=["NOUN"], help="Parts of speech to search for. Default: NOUN.")
    parser.add_argument("--output", "-o", default="part_of_speech_supercut.mp4", help="Output filename.")
    
    args = parser.parse_args()

    nlp = load_spacy_model(args.lang)

    search_words = []

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
            for token in doc:
                if token.pos_ in args.pos:
                    # ensure we're only going to grab exact words
                    search_words.append(f"^{token.text}$")

    if search_words:
        query = "|".join(search_words)
        voxgrep.voxgrep(
            args.videos, query, search_type="fragment", output=args.output
        )
    else:
        print("No matching parts of speech found.")

if __name__ == "__main__":
    main()
