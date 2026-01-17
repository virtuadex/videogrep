# Videogrep Examples

This directory contains several scripts demonstrating how to use `videogrep` as a library for more advanced and automated workflows.

## Prerequisites

- **FFmpeg**: Must be installed and in your PATH.
- **Python Dependencies**:
  ```bash
  pip install moviepy faster-whisper tqdm
  ```
- **Spacy (for NLP examples)**:
  ```bash
  pip install spacy
  python -m spacy download en_core_web_sm
  python -m spacy download pt_core_news_sm
  ```

## Included Examples

- **`auto_supercut.py`**: Automatically create a supercut from a video by selecting the most frequent non-stop words.
- **`auto_youtube.py`**: Search YouTube for a query, download the top results, transcribe them, and create a supercut.
- **`only_silence.py`**: Extract all silences (gaps between words) from a video.
- **`remove_silence.py`**: Create a new version of a video with all silences longer than a certain threshold removed.
- **`parts_of_speech.py`**: Create a supercut containing all instances of a specific part of speech (e.g., all nouns or all adjectives).
- **`pattern_matcher.py`**: Use Spacy's rule-based matching to find complex linguistic patterns (e.g., adjectives followed by nouns).

## Shared Utilities

The `utils.py` file contains shared logic for stopwords, Spacy model loading, and clip manipulation to keep the examples clean and focused.

## Usage

Most examples can be run directly from the root of the repository:

```bash
python examples/auto_supercut.py path/to/video.mp4
```
