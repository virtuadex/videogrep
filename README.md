# VoxGrep

VoxGrep is a command-line tool that searches through dialog in video or audio files and automatically generates "supercuts" based on what it finds. It supports `.srt`, `.vtt`, and `.json` (Whisper) transcriptions.

---

## 📺 Examples

- [The Meta Experience](https://www.youtube.com/watch?v=nGHbOckpifw)
- [All instances of "time" in "In Time"](https://www.youtube.com/watch?v=PQMzOUeprlk)
- [One to two second silences in "Total Recall"](https://www.youtube.com/watch?v=qEtEbXVbYJQ)
- [Press secretary telling us what he can tell us](https://www.youtube.com/watch?v=D7pymdCU5NQ)

---

## 🚀 Quick Start

### Installation

Ensure you have **Python 3.10+** and **FFmpeg** installed.

```bash
# Using Poetry (Recommended)
poetry install
poetry install --extras "full"  # For NLP features

# Using pip
pip install voxgrep
```

### Basic Usage

Search for a phrase and generate a supercut:

```bash
voxgrep --input video.mp4 --search "search phrase"
```

### ⚠️ Important: Subtitle Mapping

VoxGrep requires a matching subtitle track for every media file. **The video/audio file and subtitle file must have the exact same name**, excluding the extension:

- ✅ `movie.mp4` + `movie.srt`
- ❌ `movie.mp4` + `movie_subtitles.srt`

---

## 🎙️ Transcription

If you don't have subtitles, VoxGrep can generate them using OpenAI's Whisper.

**Built-in Transcription:**

```bash
voxgrep -i video.mp4 --transcribe --model medium
```

**Using the Automation Script:**

```bash
python auto_voxgrep.py video.mp4 "search query" --model large-v3
```

## 🖥️ Desktop Application

VoxGrep now features a premium desktop interface built with **Tauri**, **React**, and **FastAPI**.

### Features
- **Library Management:** Auto-indexing of your video/audio collection.
- **Semantic Search:** Search by concepts, not just keywords, using local AI.
- **Visual Supercut Editor:** Preview and export compilations with a high-performance UI.
- **N-Gram Analysis:** Explore linguistic patterns across your entire library.

### Development Status
The Desktop App is currently in active development. It moves away from the CLI's stateless model toward a **persistent FastAPI service** with **SQLite + Vector DB** for sub-second performance.

---

## 🛠️ CLI Options Reference

### Search & Logic

| Option          | Short | Description                                                          |
| :-------------- | :---- | :------------------------------------------------------------------- |
| `--search`      | `-s`  | Regex search term (can be used multiple times).                      |
| `--search-type` | `-st` | `sentence` (default), `fragment` (exact phrase), or `mash` (random). |
| `--max-clips`   | `-m`  | Maximum number of clips to include.                                  |
| `--randomize`   | `-r`  | Randomize clip order.                                                |

### Transcription (Whisper)

| Option           | Short  | Description                                         |
| :--------------- | :----- | :-------------------------------------------------- |
| `--transcribe`   | `-tr`  | Transcribe input using OpenAI Whisper.              |
| `--model`        | `-mo`  | Whisper model (`base`, `medium`, `large-v3`, etc.). |
| `--language`     | `-l`   | Language code (e.g., `en`, `pt`, `fr`).             |
| `--device`       | `-dev` | Device to use (`cpu` or `cuda`).                    |
| `--compute-type` | `-ct`  | Precision (`int8`, `float16`, `int8_float16`).      |

### Input & Output

| Option           | Short | Description                                                  |
| :--------------- | :---- | :----------------------------------------------------------- |
| `--input`        | `-i`  | Input file(s). Supports glob patterns.                       |
| `--output`       | `-o`  | Output filename (default: `supercut.mp4`).                   |
| `--export-clips` | `-ec` | Save clips as individual files instead of a single supercut. |
| `--export-vtt`   | `-ev` | Export the supercut transcript as a `.vtt` file.             |

### Processing & Preview

| Option         | Short | Description                                  |
| :------------- | :---- | :------------------------------------------- |
| `--padding`    | `-p`  | Seconds to add to start/end of clips.        |
| `--resyncsubs` | `-rs` | Shift subtitles forward/backward in seconds. |
| `--demo`       | `-d`  | Show results without rendering the video.    |
| `--preview`    | `-pr` | Preview the supercut in `mpv`.               |
| `--ngrams`     | `-n`  | List common words and phrases.               |

---

## 🐍 Use as a Python Module

```python
from voxgrep import voxgrep

voxgrep(
    files='video.mp4',
    query='search term',
    search_type='sentence',
    output='output.mp4'
)
```

---

## 🧪 Advanced Examples

Check the `examples/` folder for scripts covering:

- [Silence extraction](examples/only_silence.py)
- [YouTube-based supercuts](examples/auto_youtube.py)
- [POS Tagging & NLP](examples/parts_of_speech.py)
- [Spacy Pattern Matching](examples/pattern_matcher.py)

---

## 🗺️ Roadmap

- [ ] **Semantic Search:** Search by concept using vector embeddings.
- [ ] **Speaker Diarization:** Filter results by specific speakers.
- [ ] **Embedded Subtitles:** Burn-in subtitles directly onto the supercut.
- [ ] **Dynamic Transitions:** Smooth cross-fades between clips.
- [ ] **Multi-Model Support:** OpenAI API and local Apple Silicon (MLX) support.


---

## ✍️ Credits

Maintained by **virtuadex**, originally created by [Sam Lavigne](https://lav.io). Built with [MoviePy](https://zulko.github.io/moviepy/) and [OpenAI Whisper](https://github.com/openai/whisper). Special thanks to [Charlie Macquarie](https://charliemacquarie.com). Built with VoxGrep.