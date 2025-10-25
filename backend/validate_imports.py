import ast
import importlib
import os
import sys
from pathlib import Path


def check_file_imports(file_path):
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

                try:
                    module = importlib.import_module(module_name)
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        if not hasattr(module, alias.name):
                            errors.append(
                                f"ERROR: {alias.name} not found in {module_name}"
                            )
                except ImportError as e:
                    # Skip optional dependencies
                    if any(
                        opt in str(e)
                        for opt in [
                            "vosk",
                            "speech_recognition",
                            "playwright",
                            "PyPDF2",
                        ]
                    ):
                        continue
                    errors.append(f"ERROR: Cannot import {module_name}: {e}")
    except Exception as e:
        errors.append(f"ERROR: Failed to parse {file_path}: {e}")
    return errors


def main():
    sys.path.insert(0, os.getcwd())
    errors = []

    for py_file in Path("app").rglob("*.py"):
        file_errors = check_file_imports(py_file)
        if file_errors:
            print(f"FILE: {py_file}")
            for error in file_errors:
                print(f"  {error}")
            errors.extend(file_errors)

    if errors:
        print(f"\n[ERROR] Found {len(errors)} import errors")
        return 1
    else:
        print("[OK] All imports are valid")
        return 0


if __name__ == "__main__":
    exit(main())
