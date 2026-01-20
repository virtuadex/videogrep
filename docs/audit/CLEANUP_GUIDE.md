# Dead Code Cleanup - Quick Reference

## 🚀 Quick Start (3 Steps)

```bash
# Step 1: Review what will be changed
./cleanup_safe.sh

# Step 2: OR use Python script for more control
python cleanup_dead_code.py --dry-run

# Step 3: Run tests to verify
pytest
```

---

## 📋 Files to Manually Fix

### 1️⃣ `voxgrep/server/app.py` - Remove 3 unused imports

```python
# Line 17 - REMOVE:
from sqlmodel import Session, select, Query
# REPLACE WITH:
from sqlmodel import Session, select

# Line 34 - REMOVE:
from ..utils import validate_media_file

# Line 609 - REMOVE (or move to diarization endpoint when implemented):
from .diarization import assign_speakers_to_transcript
```

**Test after:** `python -m voxgrep.server.app` (should start without errors)

---

### 2️⃣ `voxgrep/server/multi_model.py` - Lazy load OpenAI

```python
# Line 259 - MOVE import inside function that uses it
# FIND the function that needs openai
# ADD at top of that function:
def function_that_uses_openai(...):
    import openai  # Import only when needed
    # ... rest of function
```

**Test after:** Ensure transcription still works

---

### 3️⃣ `voxgrep/server/subtitles.py` - Remove unused variable

```python
# Line 213 - REMOVE:
include_transitions = composition_data.get("include_transitions", True)

# OR if this is a planned feature, USE it:
if include_transitions:
    # Add transition logic
    pass
```

**Test after:** `pytest tests/ -k subtitle`

---

### 4️⃣ `voxgrep/search_engine.py` - Remove unused exception

```python
# Line 25 - REMOVE:
from .exceptions import TranscriptNotFoundError
```

**Test after:** `pytest tests/test_search.py`

---

### 5️⃣ `voxgrep/server/transitions.py` - Remove unused import

```python
# Lines 18 and 41 - REMOVE both instances:
from moviepy import CompositeAudioClip
```

**Test after:** Export a supercut with transitions

---

### 6️⃣ `voxgrep/vtt.py` - Remove unused import

```python
# Line 3 - REMOVE:
from bs4 import BeautifulSoup
```

**Test after:** `pytest tests/test_vtt_parsing.py`

---

### 7️⃣ `voxgrep/utils.py` - Remove unused imports

```python
# Remove:
import os
from typing import Optional
```

**Test after:** `pytest tests/`

---

### 8️⃣ `voxgrep/prefs.py` - Remove unused import

```python
# Remove:
import os
```

**Test after:** Run interactive mode: `voxgrep`

---

## 🔵 Design Decisions Needed

### `voxgrep/__init__.py` - Define Public API

**Current:** 35+ imports, unclear which are public API

**Option A - Minimal API:**

```python
"""VoxGrep - Semantic video search and supercut generation"""

__version__ = "3.0.0"

# Core function - main entry point
from .voxgrep import voxgrep

# Transcription
from .transcribe import transcribe

# Exporter
from .exporter import create_supercut

# Exceptions
from .exceptions import (
    VoxGrepError,
    NoResultsFoundError,
    TranscriptNotFoundError,
    SearchError,
)

__all__ = [
    "voxgrep",
    "transcribe",
    "create_supercut",
    "VoxGrepError",
    "NoResultsFoundError",
    "TranscriptNotFoundError",
    "SearchError",
    "__version__",
]
```

**Option B - Full API (current behavior):**
Keep all imports but add explicit `__all__` list.

**Recommendation:** Use Option A for cleaner API surface.

---

### `voxgrep/server/__init__.py` - Define Server API

**Recommendation:**

```python
"""VoxGrep Server - FastAPI backend for video processing"""

from .app import app
from .db import engine, create_db_and_tables, get_session
from .models import Video, SearchResult, Embedding, ExportJob

__all__ = [
    "app",
    "engine",
    "create_db_and_tables",
    "get_session",
    "Video",
    "SearchResult",
    "Embedding",
    "ExportJob",
]
```

---

## 🧪 Test Commands

After each change, run the appropriate test:

```bash
# Full test suite
pytest

# Specific modules
pytest tests/test_search.py
pytest tests/test_exporter.py
pytest tests/test_transcribe.py

# Server tests
pytest tests/test_server.py

# Run server manually
python -m voxgrep.server.app

# CLI smoke test
voxgrep --help
```

---

## 📊 Impact Analysis

| File                    | Lines Changed | Risk   | Test Command                       |
| ----------------------- | ------------- | ------ | ---------------------------------- |
| `server/app.py`         | ~3            | Medium | `python -m voxgrep.server.app`     |
| `server/multi_model.py` | ~1            | Low    | `pytest tests/test_transcribe.py`  |
| `server/subtitles.py`   | ~1            | Low    | `pytest -k subtitle`               |
| `search_engine.py`      | ~1            | Low    | `pytest tests/test_search.py`      |
| `server/transitions.py` | ~2            | Medium | Test supercut export               |
| `vtt.py`                | ~1            | Low    | `pytest tests/test_vtt_parsing.py` |
| `utils.py`              | ~2            | Low    | `pytest`                           |
| `prefs.py`              | ~1            | Low    | `voxgrep` (interactive)            |

---

## 🎯 Recommended Order

1. ✅ **Done:** Fix syntax error in `cli.py`
2. **Auto-fix:** Run `./cleanup_safe.sh` for test files
3. **Manual (Low Risk):** Fix `vtt.py`, `utils.py`, `prefs.py`
4. **Manual (Medium Risk):** Fix server files
5. **Design Decision:** Update `__init__.py` files
6. **Final:** Full test suite run

---

## 💾 Backup Before Changes

```bash
# Create backup
git add -A
git commit -m "Backup before dead code cleanup"

# Create cleanup branch
git checkout -b cleanup/remove-dead-code
```

---

## 🔄 Rollback Instructions

If something breaks:

```bash
# Rollback specific file
git checkout HEAD -- path/to/file.py

# Rollback all changes
git checkout main
git branch -D cleanup/remove-dead-code

# Or restore from backup directory
ls .backup_*  # Find latest backup
cp -r .backup_TIMESTAMP/voxgrep/* voxgrep/
```

---

## ✅ Success Criteria

- [ ] All tests pass: `pytest`
- [ ] Server starts: `python -m voxgrep.server.app`
- [ ] CLI works: `voxgrep --help`
- [ ] No lint errors: `python -m py_compile voxgrep/**/*.py`
- [ ] Git diff reviewed and approved
- [ ] Changes committed with good commit message

---

## 📈 Expected Results

- **Before:** 87 unused imports
- **After Auto-Fix:** ~10 unused imports (in tests/examples fixed)
- **After Manual Fix:** 0 unused imports
- **Code Size Reduction:** ~50-100 lines
- **Improved Maintainability:** Clearer dependencies

---

**Last Updated:** 2026-01-20  
**Status:** Ready for execution
