# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VoxGrep is a video/audio dialog search tool that creates "supercuts" from media files. It's like `grep` but for time-based media. The project consists of three main components:

1. **Python Core Library** (`voxgrep/`) - Business logic for transcription, search, and export
2. **FastAPI Server** (`voxgrep/server/`) - REST API for library management and background tasks
3. **Desktop Application** (`desktop/`) - Tauri/React GUI that communicates with the Python backend

## Build & Development Commands

### Python Development

```bash
# Install Python dependencies
poetry install

# Install with all optional features (MLX, diarization, OpenAI)
poetry install --extras full

# Run CLI
poetry run voxgrep

# Run server
poetry run voxgrep-server

# Run tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_cli_interactive.py

# Run tests matching a pattern
poetry run pytest -k "test_transcribe"
```

### Desktop GUI Development

```bash
# Install GUI dependencies
cd desktop && npm install

# Run desktop app in development mode
cd desktop && npm run tauri dev

# Or use Makefile shortcuts
make install-gui    # Install GUI dependencies
make gui           # Run GUI in dev mode
make dev           # Alias for 'make gui'
```

### Building the Desktop App

```bash
cd desktop
npm run tauri build
```

## Architecture

### Code Organization

```
voxgrep/
├── cli/              # CLI interface and interactive workflows
│   ├── main.py       # Argument parsing and CLI entry point
│   ├── interactive.py # Interactive wizard using questionary
│   ├── commands.py   # CLI command implementations
│   ├── workflows.py  # Orchestration of multi-step processes
│   ├── ngrams.py     # N-gram analysis and suggestion UI
│   ├── doctor.py     # Dependency checking and diagnostics
│   └── ui.py         # Rich console UI components
├── core/             # Core business logic
│   ├── engine.py     # Search engine (regex/exact match)
│   ├── transcriber.py # Whisper transcription (MLX/CPU/OpenAI)
│   ├── exporter.py   # MoviePy-based video export
│   ├── logic.py      # High-level voxgrep() orchestration
│   └── stream_handler.py # YouTube download and processing
├── server/           # FastAPI service
│   ├── app.py        # Main FastAPI application
│   ├── routers/      # Modular API endpoints
│   │   ├── library.py   # Library scanning and management
│   │   ├── ingest.py    # YouTube downloads and local file ingestion
│   │   ├── search.py    # Search across library
│   │   ├── export.py    # Video export operations
│   │   ├── index.py     # Semantic embedding indexing
│   │   ├── speaker.py   # Diarization endpoints
│   │   ├── media.py     # Media file serving
│   │   └── system.py    # Health, status, models
│   ├── models.py     # SQLModel database schemas
│   ├── db.py         # Database initialization
│   ├── vector_store.py # Semantic search with Sentence-Transformers
│   ├── multi_model.py  # Multi-backend transcription manager
│   ├── transitions.py  # Video transitions (crossfade, dissolve)
│   ├── subtitles.py    # Subtitle burning and presets
│   └── diarization.py  # Speaker detection (pyannote.audio)
├── formats/          # Subtitle format parsers (VTT, SRT, FCP XML)
├── utils/            # Shared utilities
│   ├── config.py     # Global config and feature flags
│   ├── helpers.py    # File validation, media type detection
│   ├── audio.py      # Audio normalization and preprocessing
│   ├── mpv_utils.py  # MPV preview functionality
│   └── exceptions.py # Custom exception classes
└── modules/          # Legacy/compatibility modules

desktop/
├── src/              # React TypeScript source
├── src-tauri/        # Rust Tauri backend
│   └── src/lib.rs    # Tauri command handlers
└── package.json      # NPM scripts and dependencies
```

### Key Architectural Patterns

**Service-Oriented Design**: The server (`voxgrep/server/`) is a persistent FastAPI service with SQLite database for library management. The desktop app communicates with this server via REST API.

**Multi-Backend Transcription**: `multi_model.py` abstracts three Whisper backends:
- **MLX** (Apple Silicon, fastest)
- **faster-whisper** (CPU/CUDA)
- **OpenAI API** (cloud fallback)

**Database-First Search**: Recent refactoring moved from file-based transcript parsing to database-driven search for performance. Transcripts are stored in the `Video` table.

**Modular Router Architecture**: Server endpoints are split into routers (`server/routers/`) rather than monolithic `app.py`. Each router handles a specific domain (library, search, export, etc.).

**Feature Flags**: Enable/disable features via `voxgrep/utils/config.py`:
- `enable_semantic_search` - Vector embeddings for concept search
- `enable_diarization` - Speaker detection
- `enable_hardware_acceleration` - GPU encoding (videotoolbox/nvenc)

### Data Flow

1. **Ingestion**: Media files are added via `/download` (YouTube) or `/add-local` (local files)
2. **Transcription**: Background task transcribes using Whisper, stores JSON in `Video.transcript_path`
3. **Indexing**: Optional semantic indexing creates embeddings stored in `Embedding` table
4. **Search**: Query matches against transcripts (regex) or embeddings (semantic)
5. **Export**: Matched segments are exported as supercut via MoviePy in `exporter.py`

### Important Conventions

**Naming Convention**: Media files and transcripts share base names:
- `movie.mp4` → `movie.json` (transcript)
- `movie.mp4` → `movie.embeddings.db` (vector index)

**Caching Strategy**:
- Transcripts are cached to avoid re-transcription
- MLX models are kept in memory after first load (`multi_model.py:MLXWhisperProvider`)
- Semantic embeddings are persisted to disk

**Hardware Acceleration**:
- Transcription: Auto-selects best device (CUDA > MLX > CPU) in `config.py`
- Export: Uses `videotoolbox` (Mac) or `nvenc` (NVIDIA) when available

## Testing

Test suite uses pytest with async support:

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test module
poetry run pytest tests/test_batch_error_recovery.py

# Run tests matching keyword
poetry run pytest -k "interactive"
```

Test coverage includes:
- CLI argument parsing and interactive modes
- Transcription error recovery and cancellation
- Batch processing error handling
- Server API endpoints (requires `httpx`)

## Dependencies

### Core Dependencies
- **moviepy 2.x**: Video editing and export
- **faster-whisper**: CPU/CUDA transcription
- **mlx-whisper**: Apple Silicon acceleration (macOS only)
- **yt-dlp**: YouTube download
- **rich**: Terminal UI styling
- **questionary**: Interactive prompts

### Server Dependencies
- **FastAPI + uvicorn**: REST API server
- **SQLModel**: Database ORM (SQLite)
- **sentence-transformers**: Semantic embeddings
- **torch**: PyTorch for ML models

### Optional Dependencies
- **pyannote.audio**: Speaker diarization (`[diarization]`)
- **spacy**: NLP utilities (`[nlp]`)
- **openai**: OpenAI API client (`[openai]`)

Install all optional features:
```bash
poetry install --extras full
```

## Desktop Application

The GUI is a **Tauri v2** application with:
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS 4
- **Backend**: Rust (Tauri commands in `src-tauri/src/lib.rs`)
- **Communication**: HTTP requests to FastAPI server on `localhost:8000`

The desktop app automatically starts the Python server on launch and manages its lifecycle.

## Database Schema

SQLite database (`voxgrep.db`) with three main tables:

**Video**
- `id`, `path`, `title`, `duration`, `source`
- `transcript_path`: Path to JSON transcript
- `transcription_status`: `pending`|`processing`|`completed`|`failed`
- `model_metadata`: JSON field tracking which Whisper model was used

**Embedding**
- `id`, `video_id`, `segment_text`, `start_time`, `end_time`
- `embedding`: Binary vector data
- Linked to `Video` via foreign key

**Speaker**
- `id`, `video_id`, `label`, `start_time`, `end_time`
- Diarization results from pyannote.audio

## Configuration

Global config is in `voxgrep/utils/config.py`:

```python
# Feature flags
enable_semantic_search = True
enable_diarization = True
enable_hardware_acceleration = True

# Server settings
host = "127.0.0.1"
port = 8000

# Paths
downloads_dir = "~/Downloads/VoxGrep"
db_path = "./voxgrep.db"

# Export settings
BATCH_SIZE = 50  # Batch large exports to prevent OOM
```

User preferences (device selection, model choice) are persisted in `voxgrep/utils/prefs.py` using a simple JSON config file.

## Common Workflows

### Adding New Search Features

1. Update search logic in `voxgrep/core/engine.py` (for regex/text)
2. Or update `voxgrep/server/vector_store.py` (for semantic search)
3. Expose via API in `voxgrep/server/routers/search.py`
4. Wire to desktop UI in `desktop/src/`

### Adding New Export Options

1. Implement in `voxgrep/core/exporter.py` using MoviePy
2. Add transition/subtitle logic in `voxgrep/server/transitions.py` or `subtitles.py`
3. Expose via `/export` endpoint in `voxgrep/server/routers/export.py`
4. Update CLI in `voxgrep/cli/commands.py` for CLI support

### Adding New Transcription Backends

1. Create provider class in `voxgrep/server/multi_model.py`
2. Implement `TranscriptionProvider` interface
3. Register in `MultiModelManager`
4. Update device detection logic in `voxgrep/utils/config.py`

## Known Issues & Quirks

- **MoviePy 2.x Migration**: Project recently migrated from MoviePy 1.x. Some legacy patterns may remain.
- **MLX Model Caching**: MLX models stay in memory after first load for performance. This can consume significant RAM.
- **Semantic Search Startup**: First semantic query is slow (~5s) due to model loading. Pre-warming happens on server startup.
- **Desktop Server Lifecycle**: Desktop app must manage Python server lifecycle carefully to avoid orphaned processes.

## Recent Major Changes

Per git history, recent work focused on:
- Desktop UI redesign with hardware acceleration
- Batch error recovery for transcription/export
- CLI interactivity improvements (interactive mode, n-gram suggestions)
- Modular project structure (split server into routers)
- MLX model caching and performance optimizations
