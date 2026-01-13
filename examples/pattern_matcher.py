import sys
import argparse
import videogrep
from videogrep import transcribe
import spacy
from spacy.matcher import Matcher


"""
Uses rule-based matching from spacy to make supercuts:
https://spacy.io/usage/rule-based-matching

Requires spacy. To install:

pip3 install spacy
python -m spacy download en_core_web_sm
python -m spacy download pt_core_news_sm
"""

def load_spacy_model(lang):
    """Tries to load the best available model for the language."""
    if lang == "en":
        models = ["en_core_web_trf", "en_core_web_lg", "en_core_web_sm"]
    else:
        models = ["pt_core_news_lg", "pt_core_news_sm"]

    for model in models:
        try:
            print(f"Attempting to load spacy model: {model}")
            return spacy.load(model)
        except OSError:
            continue
    
    print(f"Error: No spacy models found for language '{lang}'.")
    print(f"Please run: python -m spacy download {models[0]}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Uses rule-based matching from spacy to make supercuts.")
    parser.add_argument("videos", nargs="+", help="The videos we are working with")
    parser.add_argument("--lang", choices=["en", "pt"], default="en", help="Language: en or pt. Default: en.")
    
    args = parser.parse_args()

    # Enable GPU if available
    if spacy.prefer_gpu():
        print("GPU detected! Using GPU for spacy processing.")
    else:
        print("No GPU detected or spacy-transformers not configured for GPU. Using CPU.")

    nlp = load_spacy_model(args.lang)

    # grabs all instances of adjectives followed by nouns
    patterns = [[{"POS": "ADJ"}, {"POS": "NOUN"}]]

    matcher = Matcher(nlp.vocab)
    matcher.add("Patterns", patterns)


    searches = []

    for video in args.videos:
        # ensure transcript exists
        if not videogrep.find_transcript(video):
            print(f"Transcript not found for {video}. Transcribing with Whisper...")
            transcribe.transcribe(video, method="whisper")

        transcript = videogrep.parse_transcript(video)
        if not transcript:
            continue

        for sentence in transcript:
            doc = nlp(sentence["content"])
            matches = matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]  # The matched span
                searches.append(span.text)

    if searches:
        videogrep.videogrep(
            args.videos, searches, search_type="fragment", output="pattern_matcher.mp4"
        )
    else:
        print("No pattern matches found.")

if __name__ == "__main__":
    main()
