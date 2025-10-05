#!/usr/bin/env python3
"""
Comprehensive import validation script for MiraiWorks backend.
Detects unused imports, missing imports, and wrong imports.
"""
import argparse
import ast
import importlib
import sys
from pathlib import Path


class ImportValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []

        # Add project root to Python path
        sys.path.insert(0, str(self.project_root))

        # Optional dependencies that may not be installed
        self.optional_deps = {
            "vosk",
            "speech_recognition",
            "playwright",
            "PyPDF2",
            "docx",
            "pdfplumber",
            "weasyprint",
            "pdf2image",
        }

    def check_unused_imports(self, file_path: Path) -> list[str]:
        """Check for unused imports using ruff."""
        import subprocess

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    str(file_path),
                    "--select",
                    "F401",
                    "--quiet",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                return []

            unused_imports = []
            for line in result.stdout.strip().split("\n"):
                if line and "F401" in line:
                    unused_imports.append(line.strip())
            return unused_imports
        except Exception as e:
            return [f"Error checking unused imports: {e}"]

    def check_import_errors(self, file_path: Path) -> list[str]:
        """Check for import errors (missing/wrong imports)."""
        errors = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    if module_name is None:
                        continue

                    # Skip optional dependencies
                    if any(opt in module_name for opt in self.optional_deps):
                        continue

                    try:
                        module = importlib.import_module(module_name)

                        # Check each imported name
                        for alias in node.names:
                            if alias.name == "*":
                                continue

                            if not hasattr(module, alias.name):
                                errors.append(
                                    f"❌ {alias.name} not found in {module_name} "
                                    f"(line {node.lineno})"
                                )

                    except ImportError as e:
                        # Skip if it's an optional dependency
                        if any(opt in str(e) for opt in self.optional_deps):
                            continue
                        errors.append(
                            f"❌ Cannot import {module_name}: {e} (line {node.lineno})"
                        )

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            importlib.import_module(alias.name)
                        except ImportError as e:
                            if any(opt in str(e) for opt in self.optional_deps):
                                continue
                            errors.append(
                                f"❌ Cannot import {alias.name}: {e} (line {node.lineno})"
                            )

        except SyntaxError as e:
            errors.append(f"❌ Syntax error: {e}")
        except Exception as e:
            errors.append(f"❌ Error parsing file: {e}")

        return errors

    def check_import_sorting(self, file_path: Path) -> list[str]:
        """Check if imports are properly sorted."""
        import subprocess

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    str(file_path),
                    "--select",
                    "I001",
                    "--quiet",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                return []

            sorting_issues = []
            for line in result.stdout.strip().split("\n"):
                if line and "I001" in line:
                    sorting_issues.append(line.strip())
            return sorting_issues
        except Exception as e:
            return [f"Error checking import sorting: {e}"]

    def validate_file(self, file_path: Path) -> dict[str, list[str]]:
        """Validate all import aspects of a single file."""
        relative_path = file_path.relative_to(self.project_root)

        return {
            "file": str(relative_path),
            "unused_imports": self.check_unused_imports(file_path),
            "import_errors": self.check_import_errors(file_path),
            "sorting_issues": self.check_import_sorting(file_path),
        }

    def validate_project(self, app_dir: str = "app") -> dict[str, any]:
        """Validate all Python files in the project."""
        app_path = self.project_root / app_dir

        if not app_path.exists():
            return {"error": f"App directory {app_path} does not exist"}

        results = {
            "files_checked": 0,
            "files_with_issues": 0,
            "total_issues": 0,
            "file_results": [],
            "summary": {"unused_imports": 0, "import_errors": 0, "sorting_issues": 0},
        }

        for py_file in app_path.rglob("*.py"):
            # Skip __pycache__
            if "__pycache__" in str(py_file):
                continue

            results["files_checked"] += 1
            file_result = self.validate_file(py_file)

            # Count issues
            file_issue_count = (
                len(file_result["unused_imports"])
                + len(file_result["import_errors"])
                + len(file_result["sorting_issues"])
            )

            if file_issue_count > 0:
                results["files_with_issues"] += 1
                results["total_issues"] += file_issue_count
                results["file_results"].append(file_result)

                # Update summary
                results["summary"]["unused_imports"] += len(
                    file_result["unused_imports"]
                )
                results["summary"]["import_errors"] += len(file_result["import_errors"])
                results["summary"]["sorting_issues"] += len(
                    file_result["sorting_issues"]
                )

        return results

    def print_results(self, results: dict[str, any], verbose: bool = False):
        """Print validation results in a formatted way."""
        if "error" in results:
            print(f"❌ {results['error']}")
            return

        print("\n🔍 Import Validation Results")
        print(f"{'='*50}")

        # Summary
        print("📊 Summary:")
        print(f"  Files checked: {results['files_checked']}")
        print(f"  Files with issues: {results['files_with_issues']}")
        print(f"  Total issues: {results['total_issues']}")
        print(f"  Unused imports: {results['summary']['unused_imports']}")
        print(f"  Import errors: {results['summary']['import_errors']}")
        print(f"  Sorting issues: {results['summary']['sorting_issues']}")

        # File details
        if results["file_results"] and verbose:
            print("\n📋 Detailed Issues:")
            for file_result in results["file_results"]:
                print(f"\n📁 {file_result['file']}:")

                if file_result["unused_imports"]:
                    print("  🗑️ Unused imports:")
                    for issue in file_result["unused_imports"]:
                        print(f"    {issue}")

                if file_result["import_errors"]:
                    print("  ❌ Import errors:")
                    for issue in file_result["import_errors"]:
                        print(f"    {issue}")

                if file_result["sorting_issues"]:
                    print("  📝 Sorting issues:")
                    for issue in file_result["sorting_issues"]:
                        print(f"    {issue}")

        # Conclusion
        if results["total_issues"] == 0:
            print("\n✅ All imports are clean and valid!")
        else:
            print(f"\n⚠️ Found {results['total_issues']} import issues to fix.")
            print("\n🔧 Fix commands:")
            if results["summary"]["unused_imports"] > 0:
                print(
                    "  Remove unused imports: python -m ruff check app/ --select F401 --fix"
                )
            if results["summary"]["sorting_issues"] > 0:
                print("  Sort imports: python -m ruff check app/ --select I001 --fix")


def main():
    parser = argparse.ArgumentParser(
        description="Validate Python imports in MiraiWorks backend"
    )
    parser.add_argument(
        "--app-dir", default="app", help="App directory to validate (default: app)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed results"
    )
    parser.add_argument(
        "--project-root", default=".", help="Project root directory (default: current)"
    )

    args = parser.parse_args()

    validator = ImportValidator(args.project_root)
    results = validator.validate_project(args.app_dir)
    validator.print_results(results, args.verbose)

    # Exit with error code if issues found
    if results.get("total_issues", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
