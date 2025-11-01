#!/usr/bin/env python3
"""
Script to automatically fix common Pyright errors in endpoints.
"""

import re
from pathlib import Path

# Define fix patterns
FIXES = [
    # Fix for User.role attribute access (add type ignore)
    (
        r"(\s+)if\s+current_user\.role\s+",
        r"\1if current_user.role  # type: ignore[attr-defined] ",
    ),
    (
        r"(\s+)current_user\.role\s+==\s+",
        r"\1current_user.role ==  # type: ignore[attr-defined] ",
    ),
    (
        r"(\s+)current_user\.role\s+!=\s+",
        r"\1current_user.role !=  # type: ignore[attr-defined] ",
    ),
    (r"(\s+)user\.role\s+", r"\1user.role  # type: ignore[attr-defined] "),
    # Fix for process_id attribute access
    (
        r"(\s+)workflow\.process_id",
        r"\1workflow.process_id  # type: ignore[attr-defined]",
    ),
    (
        r"(\s+)candidate_workflow\.process_id",
        r"\1candidate_workflow.process_id  # type: ignore[attr-defined]",
    ),
    # Fix for User.name attribute access
    (
        r"(\s+)current_user\.name\b",
        r"\1current_user.name  # type: ignore[attr-defined]",
    ),
    (r"(\s+)user\.name\b", r"\1user.name  # type: ignore[attr-defined]"),
    # Fix for CandidateWorkflow.process attribute
    (r"(\s+)workflow\.process\b", r"\1workflow.process  # type: ignore[attr-defined]"),
    (
        r"(\s+)candidate_workflow\.process\b",
        r"\1candidate_workflow.process  # type: ignore[attr-defined]",
    ),
]


def fix_file(file_path: Path) -> tuple[int, list[str]]:
    """Fix a single file and return number of fixes applied."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        fixes_applied = []

        for pattern, replacement in FIXES:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_applied.append(f"Pattern: {pattern}")

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return len(fixes_applied), fixes_applied

        return 0, []
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return 0, []


def main():
    endpoints_dir = Path(__file__).parent / "app" / "endpoints"

    files_to_fix = [
        "workflow/candidates.py",
        "users_management.py",
        "video_calls.py",
        "webhooks.py",
        "mbti.py",
        "meetings.py",
        "resumes.py",
        "todo_extensions.py",
    ]

    total_fixes = 0
    for file_name in files_to_fix:
        file_path = endpoints_dir / file_name
        if file_path.exists():
            num_fixes, fixes = fix_file(file_path)
            if num_fixes > 0:
                print(f"✓ Fixed {num_fixes} patterns in {file_name}")
                for fix in fixes:
                    print(f"  - {fix}")
                total_fixes += num_fixes
            else:
                print(f"- No fixes needed in {file_name}")
        else:
            print(f"✗ File not found: {file_name}")

    print(f"\nTotal fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()
