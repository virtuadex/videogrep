================================================================================
VOXGREP DEAD CODE - MANUAL REVIEW CHECKLIST
================================================================================


## 🔴 HIGH PRIORITY - SYNTAX ERRORS (Fix Immediately)
--------------------------------------------------------------------------------

[ ] voxgrep/cli.py:387-388
    Issue: Duplicate 'if not search_args.preview:' statement
    Action: Remove line 388, keep line 387
    Impact: Code will not run until this is fixed


## 🟡 MEDIUM PRIORITY - Potentially Unused Code
--------------------------------------------------------------------------------

[ ] voxgrep/server/app.py:17
    Issue: Unused import 'Query'
    Action: Review if Query from SQLModel is needed for future features

[ ] voxgrep/server/app.py:34
    Issue: Unused import 'validate_media_file'
    Action: Remove if not used in API endpoints

[ ] voxgrep/server/app.py:609
    Issue: Unused import 'assign_speakers_to_transcript'
    Action: Remove if diarization feature is not implemented yet

[ ] voxgrep/server/multi_model.py:259
    Issue: Unused import 'openai'
    Action: Remove if OpenAI integration is optional and not loaded

[ ] voxgrep/server/subtitles.py:213
    Issue: Unused variable 'include_transitions'
    Action: Remove or use this variable

[ ] voxgrep/search_engine.py:25
    Issue: Unused import 'TranscriptNotFoundError'
    Action: Remove if error is not raised in this module

[ ] voxgrep/server/transitions.py:18,41
    Issue: Unused import 'CompositeAudioClip'
    Action: Remove if not needed for audio transitions


## 🔵 LOW PRIORITY - Module __init__.py Exports
--------------------------------------------------------------------------------
Note: These imports in __init__.py files are often intentional for public API.
Review each to determine if it's part of the public interface.

[ ] voxgrep/__init__.py
    - Has 35+ unused imports
    - Decision: Keep as public API or remove unused?
    - Recommendation: Create explicit __all__ list

[ ] voxgrep/server/__init__.py
    - Has 20+ unused imports
    - Decision: Keep as public API or remove unused?
    - Recommendation: Create explicit __all__ list


## 🟢 TESTS - Safe to Clean
--------------------------------------------------------------------------------

[ ] tests/test_search.py
    Action: Remove 'search_func' import if not used

[ ] tests/test_exporter.py
    Action: Remove 'pytest' and 'os' if not used

[ ] tests/test_transcribe.py
    Action: Remove 'pytest' and 'os' if not used

[ ] tests/test_vtt_parsing.py
    Action: Remove 'pytest' if not used

[ ] tests/test_search_semantic.py
    Action: Remove 'pytest' and 'os' if not used

[ ] tests/test_videogrep.py
    Action: Remove 're' and 'glob' if not used

[ ] tests/test_examples_utils.py
    Action: Remove 'pytest' if not used

[ ] tests/test_youtube.py
    Action: Remove 'MagicMock' if not used


## 📚 EXAMPLES - Low Risk
--------------------------------------------------------------------------------

[ ] examples/pattern_matcher.py
    Action: Remove 'sys' import if not used

[ ] examples/auto_supercut.py
    Action: Remove 'os' import if not used


## 🔧 UTILITY SCRIPTS
--------------------------------------------------------------------------------

[ ] auto_voxgrep.py
    Action: Remove 'subprocess' and 'Path' if not used

[ ] download_script.py
    Action: Review if this script is still needed


## 📊 SUMMARY
================================================================================
Total unused imports found: 87
Files with issues: 20+

Priority Breakdown:
  🔴 HIGH (Syntax Errors): 1 file
  🟡 MEDIUM (Unused Code): 7 issues
  🔵 LOW (__init__ exports): 2 files
  🟢 SAFE (Tests/Examples): 10 files

## 🎯 RECOMMENDED APPROACH
--------------------------------------------------------------------------------
1. Fix syntax error in cli.py immediately (BLOCKING)
2. Run automated cleanup on test files (LOW RISK)
3. Manually review and remove unused imports in main code (MEDIUM RISK)
4. Review __init__.py files and add __all__ declarations (DESIGN DECISION)
5. Run tests after each change to ensure nothing breaks
