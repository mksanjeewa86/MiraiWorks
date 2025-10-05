"""Fix Python 3.11 type annotation compatibility issues.

Replaces `type | None` syntax with `Optional[type]` to ensure compatibility.
"""
import re
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = BACKEND_DIR / "app" / "schemas"

# Pattern to match type | None syntax
PATTERN = re.compile(r"\b(\w+)\s*\|\s*None\b")


def fix_type_annotations(file_path: Path) -> tuple[bool, int]:
    """Fix type annotations in a file."""
    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # Check if Optional is already imported
    has_optional_import = "from typing import" in content and "Optional" in content

    # Find all type | None occurrences
    matches = PATTERN.findall(content)

    if not matches:
        return False, 0

    # Replace type | None with Optional[type]
    content = PATTERN.sub(r"Optional[\1]", content)

    # Ensure Optional is imported if not already
    if not has_optional_import and matches:
        # Find the typing import line
        typing_import_match = re.search(r"from typing import (.+)", content)
        if typing_import_match:
            # Add Optional to existing import
            imports = typing_import_match.group(1)
            if "Optional" not in imports:
                new_imports = imports.rstrip() + ", Optional"
                content = content.replace(
                    f"from typing import {imports}", f"from typing import {new_imports}"
                )
        else:
            # Add new typing import after other imports
            lines = content.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    insert_pos = i + 1
            lines.insert(insert_pos, "from typing import Optional")
            content = "\n".join(lines)

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        return True, len(matches)

    return False, 0


def main():
    """Fix all Python files in schemas directory."""
    total_files = 0
    total_fixes = 0

    print("Fixing type annotations in schema files...")

    for file_path in SCHEMAS_DIR.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        modified, count = fix_type_annotations(file_path)
        if modified:
            total_files += 1
            total_fixes += count
            print(f"  [OK] Fixed {count} annotations in {file_path.name}")

    print(f"\nCompleted: Fixed {total_fixes} type annotations in {total_files} files")


if __name__ == "__main__":
    main()
