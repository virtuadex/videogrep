# VoxGrep Refactoring Plan

## Overview

This document outlines the refactoring performed on the VoxGrep codebase to improve code organization, maintainability, and scalability.

## New Modules Created

### 1. `config.py` - Centralized Configuration

**Purpose**: Consolidate all configuration constants and settings

**Key Features**:

- File extension constants (SUBTITLE_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS)
- Processing constants (BATCH_SIZE, DEFAULT_PADDING)
- Transcription defaults (models, devices, compute types)
- Search defaults (semantic model, threshold)
- Server configuration (ServerConfig dataclass)
- Path utilities (get_data_dir, get_cache_dir) for XDG compliance
- Feature flags for experimental features

**Benefits**:

- Single source of truth for all configuration
- Easy to modify settings without hunting through code
- Environment variable support for paths
- Cross-platform path handling

### 2. `exceptions.py` - Exception Hierarchy

**Purpose**: Define custom exceptions for better error handling

**Exception Categories**:

- **Base**: `VoxGrepError`
- **File/IO**: `FileNotFoundError`, `TranscriptNotFoundError`, `InvalidFileFormatError`
- **Transcription**: `TranscriptionError`, `TranscriptionModelNotAvailableError`, `TranscriptionFailedError`
- **Search**: `SearchError`, `NoResultsFoundError`, `InvalidSearchTypeError`, `SemanticSearchNotAvailableError`
- **Export**: `ExportError`, `InvalidOutputFormatError`, `ExportFailedError`
- **Server**: `ServerError`, `DatabaseError`, `LibraryScanError`

**Benefits**:

- Precise error handling and debugging
- Better error messages for users
- Easier to catch and handle specific error types

### 3. `utils.py` - Utility Functions

**Purpose**: Common utility functions used across the application

**Function Categories**:

- **File Type Detection**: `is_video_file()`, `is_audio_file()`, `is_media_file()`, `get_media_type()`
- **Path Utilities**: `ensure_absolute_path()`, `ensure_directory_exists()`, `get_base_filename()`
- **File Validation**: `validate_file_exists()`, `validate_media_file()`
- **List Utilities**: `ensure_list()`, `flatten_list()`
- **String Utilities**: `format_time()`, `format_file_size()`
- **Logging**: `setup_logger()` with consistent formatting

**Benefits**:

- Reduces code duplication
- Consistent behavior across modules
- Easier to test and maintain

## Refactoring Applied to Existing Modules

### `search_engine.py`

**Changes**:

1. ✅ Updated imports to use `config`, `utils`, and `exceptions` modules
2. ✅ Replaced hardcoded constants with config imports
3. ✅ Added comprehensive docstrings to all functions
4. ✅ Enhanced `SemanticModel` class with better error handling
5. ✅ Improved `find_transcript()` with better documentation and strategy comments
6. ✅ Enhanced `parse_transcript()` and `get_embeddings()` with full docstrings
7. 🔄 TODO: Refactor `search()` function to use `ensure_list()` and custom exceptions
8. 🔄 TODO: Add type hints for return types in search functions

### `transcribe.py`

**Planned Changes**:

1. Import from `config` for model defaults
2. Use custom exceptions for better error handling
3. Add comprehensive docstrings
4. Use `setup_logger()` from utils
5. Improve error messages

### `exporter.py`

**Planned Changes**:

1. Import BATCH_SIZE from config
2. Use file type utilities from utils
3. Add better error handling with custom exceptions
4. Improve progress reporting

### `voxgrep.py`

**Planned Changes**:

1. Use config for default padding values
2. Better separation of concerns
3. Improve error handling
4. Add comprehensive docstrings

### `cli.py`

**Planned Changes**:

1. Use config for all defaults
2. Better argument validation
3. Improved error messages using custom exceptions

### `server/app.py`

**Planned Changes**:

1. Use ServerConfig from config
2. Better error handling with custom exceptions
3. Improved logging
4. Better separation of concerns (move business logic to service layer)

### `server/db.py`

**Planned Changes**:

1. Use get_data_dir() from config for database location
2. Better error handling

## Architecture Improvements

### Service Layer Pattern

Create a new `services/` directory with:

- `transcription_service.py` - Handles all transcription logic
- `search_service.py` - Handles all search logic
- `export_service.py` - Handles all export logic
- `library_service.py` - Handles library management

**Benefits**:

- Clear separation between API, business logic, and data access
- Easier to test
- Reusable across CLI and server

### Type Safety

- Add comprehensive type hints to all functions
- Use `TypedDict` for segment dictionaries
- Consider using Pydantic models for validation

### Testing Infrastructure

Create `tests/` directory with:

- Unit tests for each module
- Integration tests for workflows
- Test fixtures and utilities

## Migration Guide

### For Developers Using VoxGrep as a Library

**Before**:

```python
from voxgrep import search_engine

# Hardcoded values
results = search_engine.search(files, query, threshold=0.45)
```

**After**:

```python
from voxgrep import search_engine
from voxgrep.config import DEFAULT_SEMANTIC_THRESHOLD
from voxgrep.exceptions import NoResultsFoundError

try:
    results = search_engine.search(files, query, threshold=DEFAULT_SEMANTIC_THRESHOLD)
except NoResultsFoundError as e:
    print(f"No results: {e}")
```

### Backwards Compatibility

All existing public APIs remain unchanged. New modules are additive only.

**Legacy constants maintained**:

- `search_engine.SUB_EXTS` still available (points to `config.SUBTITLE_EXTENSIONS`)
- `exporter.BATCH_SIZE` still available (points to `config.BATCH_SIZE`)

## Next Steps

1. ✅ Create `config.py`, `exceptions.py`, `utils.py`
2. ✅ Update `search_engine.py` imports and basic refactoring
3. 🔄 Complete `search_engine.py` refactoring (search function)
4. 🔄 Refactor `transcribe.py`
5. 🔄 Refactor `exporter.py`
6. 🔄 Refactor `voxgrep.py`
7. 🔄 Refactor `cli.py`
8. 🔄 Refactor `server/` modules
9. 🔄 Create service layer
10. 🔄 Add comprehensive tests
11. 🔄 Update documentation

## Benefits Summary

1. **Maintainability**: Easier to find and modify code
2. **Testability**: Smaller, focused functions are easier to test
3. **Scalability**: Clear architecture supports future features
4. **Developer Experience**: Better error messages and documentation
5. **Performance**: No performance impact, only organizational improvements
6. **Backwards Compatibility**: Existing code continues to work
