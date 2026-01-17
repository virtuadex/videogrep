# Gemini Project Context: VoxGrep

This document provides essential context for Gemini to understand and work with the `voxgrep` project.

## Project Overview

**VoxGrep** is a command-line tool designed to search through dialog in video and audio files and automatically generate "supercuts" (compilations of clips) based on matching search queries. It functions like `grep`, but for time-based media.

### Key Features

- **Regex Search:** Search for phrases or patterns using regular expressions in subtitle tracks or transcriptions.
- **Transcription Support:** Automatically transcribe media using **OpenAI Whisper** (via `faster-whisper`), or **Pocketsphinx**.
- **Multiple Search Types:**
  - `sentence`: Clips containing full sentences matching the query.
  - `fragment`: Precise word or phrase matching (requires word-level timestamps).
  - `mash`: Randomly selects instances of specific words to create a "mashup".
- **Export Formats:** Supports `.mp4`, `.mp3`, `.m3u` (playlists), `.mpv.edl` (previews), and `.xml` (Final Cut Pro/Premiere/Resolve timelines).
- **Automation:** Includes `auto_voxgrep.py` for a seamless "transcribe then search" workflow.

### Core Technologies

- **Language:** Python 3.10+
- **Media Engine:** [MoviePy 2.x](https://zulko.github.io/moviepy/) (utilizes FFmpeg and NumPy 2.0+).
- **Transcription:** OpenAI Whisper (optimized via `faster-whisper` for high performance).
- **Dependency Management:** [Poetry](https://python-poetry.org/).
- **Subtitle Parsing:** Custom parsers for `.srt`, `.vtt`, and `.json`.

---

## Project Architecture

VoxGrep is evolving from a pure CLI tool into a **Service-Oriented Desktop Application**.

### Current Components
- `voxgrep/`: The core logic for searching, padding, and concatenation.
- `desktop_api.py`: (Legacy) IPC bridge for the GUI. **[To be deprecated]**
- `desktop/`: Tauri-based GUI (React + Vite).

### Future Architecture (In Progress)
- **Backend Service:** FastAPI (Python) running a local REST/WebSocket server.
- **Database Layer:** 
  - **SQLite:** Metadata storage for the video library and transcripts.
  - **Vector DB:** Integrated vector database (SQLite-vss or LanceDB) for lightning-fast semantic searches across the entire library.
- **State Management:** TanStack Query on the frontend for robust caching and server-state synchronization.
- **Persistent AI Models:** Whisper and Sentence-Transformers stay resident in memory within the FastAPI process for sub-second search responses.

---

## Development Conventions

- **Service Architecture:** Prefer adding new functionality to the FastAPI endpoints rather than the CLI entry point.
- **Local-First AI:** All AI processing remains local. No video or transcripts should leave the user's machine.
- **Subtitles Mapping:** `voxgrep` expects subtitle/transcript files to have the _exact same name_ as the media file.
- **Memory Management:** Use `create_supercut_in_batches` for large supercuts.

---

## Current Roadmap

### Phase 1: Foundation (Current)
- [x] Modern UI/UX implementation (Framer Motion + Tailwind).
- [ ] **Migration to FastAPI:** Replace the subprocess-based IPC with a persistent REST API.
- [ ] **SQLite Database:** Implement a central database to index the library.

### Phase 2: Semantic Power
- [ ] **Vector Indexing:** Automatically generate and store embeddings in a vector DB on import.
- [ ] **Cross-Library Search:** Search across all indexed videos simultaneously.
- [ ] **Speaker Diarization:** Identify and filter results by specific speakers.

### Phase 3: Advanced Media
- [ ] **Dynamic Transitions:** Support for cross-fades and audio smoothing.
- [ ] **Embedded Subtitles:** Option to burn-in subtitles directly onto clips.
- [ ] **Multi-Model Support:** Integration with MLX-Whisper and Apple Silicon optimizations.