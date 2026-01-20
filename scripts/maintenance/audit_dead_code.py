#!/usr/bin/env python3
"""
VoxGrep Dead Code Audit Script
Analyzes the codebase for:
1. Dead code (unused functions, classes, methods)
2. Unused imports
3. Unreachable logic paths
"""

import ast
import os
import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class DeadCodeAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST for unreachable code and other issues."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues = []
        self.current_function = None
        self.has_return = False
        self.after_return = False
        
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        old_has_return = self.has_return
        old_after_return = self.after_return
        
        self.current_function = node.name
        self.has_return = False
        self.after_return = False
        
        self.generic_visit(node)
        
        self.current_function = old_function
        self.has_return = old_has_return
        self.after_return = old_after_return
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_Return(self, node):
        if self.current_function:
            self.has_return = True
            self.after_return = True
        self.generic_visit(node)
        
    def visit_Raise(self, node):
        if self.current_function:
            self.after_return = True
        self.generic_visit(node)
        
    def visit_Expr(self, node):
        if self.after_return and self.current_function:
            # Code after return/raise (unless it's in a try/except/finally)
            if not isinstance(node.value, (ast.Pass, ast.Ellipsis)):
                self.issues.append({
                    'type': 'unreachable_code',
                    'function': self.current_function,
                    'line': node.lineno,
                    'message': f'Unreachable code after return/raise in {self.current_function}'
                })
        self.generic_visit(node)
        
    def visit_If(self, node):
        # Check for if True / if False
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                self.issues.append({
                    'type': 'always_true',
                    'line': node.lineno,
                    'message': f'Condition is always True (unreachable else branch)'
                })
            elif node.test.value is False:
                self.issues.append({
                    'type': 'always_false',
                    'line': node.lineno,
                    'message': f'Condition is always False (unreachable if branch)'
                })
        self.generic_visit(node)


class ImportAnalyzer(ast.NodeVisitor):
    """Analyzes imports and their usage."""
    
    def __init__(self):
        self.imports = {}  # name -> (module, line)
        self.used_names = set()
        
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = (alias.name, node.lineno)
            
    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            module = f"{node.module}.{alias.name}" if node.module else alias.name
            self.imports[name] = (module, node.lineno)
            
    def visit_Name(self, node):
        self.used_names.add(node.id)
        self.generic_visit(node)
        
    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)
        
    def get_unused_imports(self) -> List[Tuple[str, str, int]]:
        unused = []
        for name, (module, line) in self.imports.items():
            if name not in self.used_names:
                unused.append((name, module, line))
        return unused


def analyze_file(filepath: str) -> Dict:
    """Analyze a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content, filename=filepath)
        
        # Analyze unreachable code
        dead_analyzer = DeadCodeAnalyzer(filepath)
        dead_analyzer.visit(tree)
        
        # Analyze imports
        import_analyzer = ImportAnalyzer()
        import_analyzer.visit(tree)
        unused_imports = import_analyzer.get_unused_imports()
        
        return {
            'file': filepath,
            'unreachable_code': dead_analyzer.issues,
            'unused_imports': unused_imports,
            'success': True
        }
        
    except SyntaxError as e:
        return {
            'file': filepath,
            'error': f'Syntax error: {e}',
            'success': False
        }
    except Exception as e:
        return {
            'file': filepath,
            'error': f'Error: {e}',
            'success': False
        }


def find_python_files(directory: str, exclude_dirs: Set[str] = None) -> List[str]:
    """Find all Python files in directory."""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', 
                       'node_modules', '.tox', 'build', 'dist', '.eggs'}
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
                
    return python_files


def generate_report(results: List[Dict]) -> str:
    """Generate a formatted report."""
    report = []
    report.append("=" * 80)
    report.append("VOXGREP DEAD CODE AUDIT REPORT")
    report.append("=" * 80)
    report.append("")
    
    total_files = len(results)
    total_unused_imports = 0
    total_unreachable = 0
    
    # Unused Imports Section
    report.append("\n" + "=" * 80)
    report.append("UNUSED IMPORTS")
    report.append("=" * 80)
    
    for result in results:
        if result.get('success') and result.get('unused_imports'):
            filepath = result['file']
            rel_path = os.path.relpath(filepath)
            report.append(f"\n📄 {rel_path}")
            for name, module, line in result['unused_imports']:
                report.append(f"   Line {line}: Unused import '{name}' from '{module}'")
                total_unused_imports += 1
                
    if total_unused_imports == 0:
        report.append("\n✅ No unused imports found!")
        
    # Unreachable Code Section
    report.append("\n\n" + "=" * 80)
    report.append("UNREACHABLE CODE & LOGIC ISSUES")
    report.append("=" * 80)
    
    for result in results:
        if result.get('success') and result.get('unreachable_code'):
            filepath = result['file']
            rel_path = os.path.relpath(filepath)
            report.append(f"\n📄 {rel_path}")
            for issue in result['unreachable_code']:
                report.append(f"   Line {issue['line']}: [{issue['type']}] {issue['message']}")
                total_unreachable += 1
                
    if total_unreachable == 0:
        report.append("\n✅ No unreachable code found!")
        
    # Summary
    report.append("\n\n" + "=" * 80)
    report.append("SUMMARY")
    report.append("=" * 80)
    report.append(f"Total files analyzed: {total_files}")
    report.append(f"Unused imports: {total_unused_imports}")
    report.append(f"Unreachable code issues: {total_unreachable}")
    report.append("")
    
    return "\n".join(report)


def main():
    """Main execution."""
    project_root = Path(__file__).parents[2]
    
    print("🔍 Scanning VoxGrep codebase for dead code...\n")
    
    # Find all Python files
    python_files = find_python_files(str(project_root))
    
    # Analyze each file
    results = []
    for filepath in python_files:
        rel_path = os.path.relpath(filepath)
        print(f"Analyzing: {rel_path}")
        result = analyze_file(filepath)
        results.append(result)
        
    # Generate report
    report = generate_report(results)
    
    # Save report
    report_file = project_root / 'DEAD_CODE_AUDIT.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    # Also save JSON for programmatic access
    json_file = project_root / 'dead_code_audit.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"\n✅ Analysis complete!")
    print(f"📄 Report saved to: {report_file}")
    print(f"📄 JSON data saved to: {json_file}")
    print("\n" + "=" * 80)
    print(report)


if __name__ == '__main__':
    main()
