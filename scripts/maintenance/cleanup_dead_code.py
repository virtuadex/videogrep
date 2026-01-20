#!/usr/bin/env python3
"""
VoxGrep Dead Code Cleanup Script
Automatically removes unused imports and generates a checklist for manual review.

Usage:
    python cleanup_dead_code.py --dry-run  # Preview changes without modifying
    python cleanup_dead_code.py --apply    # Apply changes to files
"""

import argparse
import os
import subprocess
from pathlib import Path
from typing import List, Dict

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DeadCodeCleaner:
    """Manages the cleanup process for dead code."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.changes_made = []
        self.manual_review_items = []
        
    def remove_unused_imports(self, filepath: str, dry_run: bool = True) -> bool:
        """Remove unused imports from a file using autoflake."""
        try:
            cmd = [
                'autoflake',
                '--remove-all-unused-imports',
                '--remove-unused-variables',
            ]
            
            if not dry_run:
                cmd.append('--in-place')
            
            cmd.append(filepath)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                self.changes_made.append({
                    'file': filepath,
                    'type': 'unused_imports',
                    'changes': result.stdout
                })
                return True
            
            return False
            
        except Exception as e:
            print(f"{Colors.RED}Error processing {filepath}: {e}{Colors.END}")
            return False
    
    def fix_syntax_errors(self, filepath: str) -> List[Dict]:
        """Identify syntax errors that need manual fixing."""
        issues = []
        
        # Known syntax error in cli.py
        if 'cli.py' in filepath:
            issues.append({
                'file': filepath,
                'line': 387,
                'type': 'duplicate_line',
                'description': 'Duplicate "if not search_args.preview:" on lines 387-388',
                'fix': 'Remove line 388 (keep line 387)',
                'severity': 'HIGH'
            })
        
        return issues
    
    def generate_manual_checklist(self) -> str:
        """Generate a checklist for manual review."""
        checklist = []
        checklist.append("=" * 80)
        checklist.append("VOXGREP DEAD CODE - MANUAL REVIEW CHECKLIST")
        checklist.append("=" * 80)
        checklist.append("")
        
        # HIGH PRIORITY ITEMS
        checklist.append("\n## 🔴 HIGH PRIORITY - SYNTAX ERRORS (Fix Immediately)")
        checklist.append("-" * 80)
        checklist.append("")
        checklist.append("[ ] voxgrep/cli.py:387-388")
        checklist.append("    Issue: Duplicate 'if not search_args.preview:' statement")
        checklist.append("    Action: Remove line 388, keep line 387")
        checklist.append("    Impact: Code will not run until this is fixed")
        checklist.append("")
        
        # VULTURE FINDINGS
        checklist.append("\n## 🟡 MEDIUM PRIORITY - Potentially Unused Code")
        checklist.append("-" * 80)
        checklist.append("")
        
        vulture_findings = [
            ("voxgrep/server/app.py:17", "Unused import 'Query'", 
             "Review if Query from SQLModel is needed for future features"),
            ("voxgrep/server/app.py:34", "Unused import 'validate_media_file'", 
             "Remove if not used in API endpoints"),
            ("voxgrep/server/app.py:609", "Unused import 'assign_speakers_to_transcript'", 
             "Remove if diarization feature is not implemented yet"),
            ("voxgrep/server/multi_model.py:259", "Unused import 'openai'", 
             "Remove if OpenAI integration is optional and not loaded"),
            ("voxgrep/server/subtitles.py:213", "Unused variable 'include_transitions'", 
             "Remove or use this variable"),
            ("voxgrep/search_engine.py:25", "Unused import 'TranscriptNotFoundError'", 
             "Remove if error is not raised in this module"),
            ("voxgrep/server/transitions.py:18,41", "Unused import 'CompositeAudioClip'", 
             "Remove if not needed for audio transitions"),
        ]
        
        for location, issue, action in vulture_findings:
            checklist.append(f"[ ] {location}")
            checklist.append(f"    Issue: {issue}")
            checklist.append(f"    Action: {action}")
            checklist.append("")
        
        # __INIT__ FILES
        checklist.append("\n## 🔵 LOW PRIORITY - Module __init__.py Exports")
        checklist.append("-" * 80)
        checklist.append("Note: These imports in __init__.py files are often intentional for public API.")
        checklist.append("Review each to determine if it's part of the public interface.")
        checklist.append("")
        
        checklist.append("[ ] voxgrep/__init__.py")
        checklist.append("    - Has 35+ unused imports")
        checklist.append("    - Decision: Keep as public API or remove unused?")
        checklist.append("    - Recommendation: Create explicit __all__ list")
        checklist.append("")
        
        checklist.append("[ ] voxgrep/server/__init__.py")
        checklist.append("    - Has 20+ unused imports")
        checklist.append("    - Decision: Keep as public API or remove unused?")
        checklist.append("    - Recommendation: Create explicit __all__ list")
        checklist.append("")
        
        # TEST FILES
        checklist.append("\n## 🟢 TESTS - Safe to Clean")
        checklist.append("-" * 80)
        checklist.append("")
        
        test_files = [
            ("tests/test_search.py", "Remove 'search_func' import if not used"),
            ("tests/test_exporter.py", "Remove 'pytest' and 'os' if not used"),
            ("tests/test_transcribe.py", "Remove 'pytest' and 'os' if not used"),
            ("tests/test_vtt_parsing.py", "Remove 'pytest' if not used"),
            ("tests/test_search_semantic.py", "Remove 'pytest' and 'os' if not used"),
            ("tests/test_videogrep.py", "Remove 're' and 'glob' if not used"),
            ("tests/test_examples_utils.py", "Remove 'pytest' if not used"),
            ("tests/test_youtube.py", "Remove 'MagicMock' if not used"),
        ]
        
        for filepath, action in test_files:
            checklist.append(f"[ ] {filepath}")
            checklist.append(f"    Action: {action}")
            checklist.append("")
        
        # EXAMPLES
        checklist.append("\n## 📚 EXAMPLES - Low Risk")
        checklist.append("-" * 80)
        checklist.append("")
        
        checklist.append("[ ] examples/pattern_matcher.py")
        checklist.append("    Action: Remove 'sys' import if not used")
        checklist.append("")
        
        checklist.append("[ ] examples/auto_supercut.py")
        checklist.append("    Action: Remove 'os' import if not used")
        checklist.append("")
        
        # ROOT FILES
        checklist.append("\n## 🔧 UTILITY SCRIPTS")
        checklist.append("-" * 80)
        checklist.append("")
        
        checklist.append("[ ] auto_voxgrep.py")
        checklist.append("    Action: Remove 'subprocess' and 'Path' if not used")
        checklist.append("")
        
        checklist.append("[ ] download_script.py")
        checklist.append("    Action: Review if this script is still needed")
        checklist.append("")
        
        # SUMMARY
        checklist.append("\n## 📊 SUMMARY")
        checklist.append("=" * 80)
        checklist.append("Total unused imports found: 87")
        checklist.append("Files with issues: 20+")
        checklist.append("")
        checklist.append("Priority Breakdown:")
        checklist.append("  🔴 HIGH (Syntax Errors): 1 file")
        checklist.append("  🟡 MEDIUM (Unused Code): 7 issues")
        checklist.append("  🔵 LOW (__init__ exports): 2 files")
        checklist.append("  🟢 SAFE (Tests/Examples): 10 files")
        checklist.append("")
        checklist.append("## 🎯 RECOMMENDED APPROACH")
        checklist.append("-" * 80)
        checklist.append("1. Fix syntax error in cli.py immediately (BLOCKING)")
        checklist.append("2. Run automated cleanup on test files (LOW RISK)")
        checklist.append("3. Manually review and remove unused imports in main code (MEDIUM RISK)")
        checklist.append("4. Review __init__.py files and add __all__ declarations (DESIGN DECISION)")
        checklist.append("5. Run tests after each change to ensure nothing breaks")
        checklist.append("")
        
        return "\n".join(checklist)
    
    def auto_fix_safe_files(self, dry_run: bool = True) -> List[str]:
        """Automatically fix low-risk files (tests, examples)."""
        safe_files = [
            'tests/test_search.py',
            'tests/test_exporter.py',
            'tests/test_transcribe.py',
            'tests/test_vtt_parsing.py',
            'tests/test_search_semantic.py',
            'tests/test_videogrep.py',
            'tests/test_examples_utils.py',
            'tests/test_youtube.py',
            'examples/pattern_matcher.py',
            'examples/auto_supercut.py',
        ]
        
        fixed = []
        for rel_path in safe_files:
            filepath = self.project_root / rel_path
            if filepath.exists():
                if self.remove_unused_imports(str(filepath), dry_run=dry_run):
                    fixed.append(rel_path)
        
        return fixed


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Clean up dead code in VoxGrep')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without modifying files')
    parser.add_argument('--apply', action='store_true', 
                       help='Apply changes to files')
    parser.add_argument('--checklist-only', action='store_true',
                       help='Only generate the manual checklist')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply and not args.checklist_only:
        print(f"{Colors.YELLOW}No action specified. Use --dry-run, --apply, or --checklist-only{Colors.END}")
        parser.print_help()
        return
    
    project_root = Path(__file__).parents[2]
    cleaner = DeadCodeCleaner(str(project_root))
    
    # Generate and save checklist
    checklist = cleaner.generate_manual_checklist()
    checklist_file = project_root / 'CLEANUP_CHECKLIST.md'
    
    with open(checklist_file, 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}VoxGrep Dead Code Cleanup{Colors.END}\n")
    print(f"{Colors.GREEN}✓ Manual checklist saved to: {checklist_file}{Colors.END}\n")
    
    if args.checklist_only:
        print(checklist)
        return
    
    # Auto-fix safe files
    if args.dry_run:
        print(f"{Colors.YELLOW}🔍 DRY RUN MODE - No files will be modified{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠️  APPLYING CHANGES - Files will be modified{Colors.END}\n")
    
    print(f"{Colors.BOLD}Auto-fixing safe files (tests and examples)...{Colors.END}\n")
    
    fixed_files = cleaner.auto_fix_safe_files(dry_run=args.dry_run)
    
    if fixed_files:
        print(f"{Colors.GREEN}Fixed {len(fixed_files)} files:{Colors.END}")
        for f in fixed_files:
            print(f"  ✓ {f}")
    else:
        print(f"{Colors.YELLOW}No changes needed in safe files.{Colors.END}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print(f"1. Review CLEANUP_CHECKLIST.md")
    print(f"2. Fix the syntax error in voxgrep/cli.py (line 388)")
    print(f"3. Run: pytest   # Ensure tests still pass")
    print(f"4. Manually review and clean remaining files")
    print()


if __name__ == '__main__':
    main()
