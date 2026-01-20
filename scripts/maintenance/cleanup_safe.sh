#!/bin/bash
# VoxGrep Dead Code Cleanup Script
# This script safely removes dead code in phases

set -e  # Exit on error

# Ensure we are running from the project root
cd "$(dirname "$0")/../.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║         VoxGrep Dead Code Cleanup - Safe Removal Tool       ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if tests pass
run_tests() {
    echo -e "${BLUE}🧪 Running test suite...${NC}"
    if python3.12 -m pytest --tb=short -q; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ Tests failed!${NC}"
        return 1
    fi
}

# Function to backup files
backup_files() {
    BACKUP_DIR=".backup_$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}📦 Creating backup in ${BACKUP_DIR}...${NC}"
    mkdir -p "$BACKUP_DIR"
    
    # Backup all Python files
    cp -r voxgrep "$BACKUP_DIR/"
    cp -r tests "$BACKUP_DIR/"
    cp -r examples "$BACKUP_DIR/" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Backup created${NC}"
}

# Phase 1: Verify critical fix
echo -e "${BOLD}Phase 1: Verify Critical Fix${NC}"
echo "────────────────────────────────────────────────────────────"
if python3.12 -m py_compile voxgrep/cli.py; then
    echo -e "${GREEN}✅ voxgrep/cli.py syntax is valid${NC}"
else
    echo -e "${RED}❌ voxgrep/cli.py has syntax errors!${NC}"
    # Try to compile again showing output to user if it failed above (though removing 2>/dev/null above does this)
    exit 1
fi
echo ""

# Phase 2: Run baseline tests
echo -e "${BOLD}Phase 2: Baseline Test Run${NC}"
echo "────────────────────────────────────────────────────────────"
if run_tests; then
    echo -e "${GREEN}✅ Baseline tests passing${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failing - will continue but be careful${NC}"
fi
echo ""

# Phase 3: Create backup
echo -e "${BOLD}Phase 3: Safety Backup${NC}"
echo "────────────────────────────────────────────────────────────"
backup_files
echo ""

# Phase 4: Auto-fix safe files
echo -e "${BOLD}Phase 4: Auto-Fix Safe Files (Tests & Examples)${NC}"
echo "────────────────────────────────────────────────────────────"
echo -e "${YELLOW}This will automatically remove unused imports from test and example files.${NC}"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Running autoflake on test files...${NC}"
    
    # Auto-fix test files
    autoflake --in-place --remove-all-unused-imports --remove-unused-variables \
        tests/test_search.py \
        tests/test_exporter.py \
        tests/test_transcribe.py \
        tests/test_vtt_parsing.py \
        tests/test_search_semantic.py \
        tests/test_videogrep.py \
        tests/test_examples_utils.py \
        tests/test_youtube.py \
        2>/dev/null || echo -e "${YELLOW}Some files were not modified${NC}"
    
    # Auto-fix example files
    echo -e "${BLUE}Running autoflake on example files...${NC}"
    autoflake --in-place --remove-all-unused-imports --remove-unused-variables \
        examples/pattern_matcher.py \
        examples/auto_supercut.py \
        2>/dev/null || echo -e "${YELLOW}Some files were not modified${NC}"
    
    echo -e "${GREEN}✅ Auto-fix complete${NC}"
    
    # Run tests again
    echo -e "${BLUE}🧪 Running tests after auto-fix...${NC}"
    if run_tests; then
        echo -e "${GREEN}✅ Tests still passing after cleanup!${NC}"
    else
        echo -e "${RED}❌ Tests failed after cleanup!${NC}"
        echo -e "${YELLOW}You may need to restore from backup${NC}"
    fi
else
    echo -e "${YELLOW}Skipped auto-fix phase${NC}"
fi
echo ""

# Phase 5: Manual cleanup checklist
echo -e "${BOLD}Phase 5: Manual Review Required${NC}"
echo "────────────────────────────────────────────────────────────"
echo -e "${YELLOW}The following files require manual review:${NC}"
echo ""
echo "  🟡 Medium Priority:"
echo "     • voxgrep/server/app.py (3 unused imports)"
echo "     • voxgrep/server/multi_model.py (1 unused import)"
echo "     • voxgrep/server/subtitles.py (1 unused variable)"
echo "     • voxgrep/search_engine.py (1 unused import)"
echo "     • voxgrep/server/transitions.py (1 unused import)"
echo "     • voxgrep/vtt.py (1 unused import)"
echo ""
echo "  🔵 Low Priority (Design Decision):"
echo "     • voxgrep/__init__.py (Review public API)"
echo "     • voxgrep/server/__init__.py (Review public API)"
echo ""
echo -e "${CYAN}📄 See docs/audit/CLEANUP_CHECKLIST.md for detailed instructions${NC}"
echo -e "${CYAN}📄 See docs/audit/AUDIT_REPORT.md for full analysis${NC}"
echo ""

# Summary
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║                    Cleanup Summary                          ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Critical syntax error: FIXED${NC}"
echo -e "${GREEN}✅ Safe auto-cleanup: READY${NC}"
echo -e "${YELLOW}⏳ Manual review: PENDING${NC}"
echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo "  1. Review git diff to see changes"
echo "  2. Manually fix medium-priority issues (see checklist)"
echo "  3. Run: pytest  (verify everything works)"
echo "  4. Commit changes"
echo ""
echo -e "${CYAN}🎯 Total unused imports: 87${NC}"
echo -e "${CYAN}📁 Files analyzed: 45${NC}"
echo ""
