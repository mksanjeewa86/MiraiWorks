#!/usr/bin/env python3
"""
Fix remaining test errors in interviews and other files
"""
import re
from pathlib import Path

BACKEND_DIR = Path(__file__).parent

def fix_file_with_patterns(filepath, fixes):
    """Apply a list of regex fixes to a file"""
    if not filepath.exists():
        print(f"  Skipping {filepath.name} - not found")
        return False

    content = filepath.read_text(encoding="utf-8")
    original = content

    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        print(f"  ✓ Fixed {filepath.name}")
        return True
    else:
        print(f"  - No changes needed for {filepath.name}")
        return False

def fix_interviews():
    """Fix interview test files"""
    print("\n=== Fixing interview test files ===")

    files = [
        "test_interviews.py",
        "test_interviews_comprehensive.py",
        "test_recruitment_scenario.py",
        "test_recruitment_workflows.py",
    ]

    for filename in files:
        filepath = BACKEND_DIR / "app" / "tests" / filename

        fixes = [
            # Add assertion after company_id assignment from test_employer_user
            (
                r'([ \t]+)(company_id = test_employer_user\.company_id)\n',
                r'\1\2\n\1assert company_id is not None\n'
            ),
            # Add assertion after company_id assignment from test_company
            (
                r'([ \t]+)(company_id = test_company\.id)\n',
                r'\1\2\n\1assert company_id is not None\n'
            ),
            # Add assertion after getting interview that might be None
            (
                r'([ \t]+)(interview = await .*?get.*?\(.*?\))\n([ \t]+)(assert interview\.)',
                r'\1\2\n\1assert interview is not None\n\3\4'
            ),
            # Change return type hint from Interview | None to Interview (will add assertion)
            (
                r'-> tuple\[Interview \| None,',
                r'-> tuple[Interview,'
            ),
        ]

        fix_file_with_patterns(filepath, fixes)

def fix_video_calls():
    """Fix video call test files"""
    print("\n=== Fixing video call test files ===")

    filepath = BACKEND_DIR / "app" / "tests" / "test_video_calls.py"

    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # If we see response.json(), add assertion after
        if "response.json()" in line and "=" in line:
            var_name = line.split("=")[0].strip()
            indent = len(line) - len(line.lstrip())
            # Check if next line doesn't already have assertion
            if i + 1 < len(lines) and "assert" not in lines[i + 1]:
                new_lines.append(" " * indent + f"assert {var_name} is not None")

        i += 1

    content = "\n".join(new_lines)
    filepath.write_text(content, encoding="utf-8")
    print(f"  ✓ Fixed test_video_calls.py")

def fix_recruitment_workflow_models():
    """Fix recruitment workflow models test"""
    print("\n=== Fixing recruitment workflow models ===")

    filepath = BACKEND_DIR / "app" / "tests" / "test_recruitment_workflow_models.py"

    fixes = [
        # Add assertion before accessing subscript
        (
            r'([ \t]+)(assert workflow_data\[)',
            r'\1assert workflow_data is not None\n\1\2'
        ),
    ]

    fix_file_with_patterns(filepath, fixes)

def fix_permission_matrix_unbound():
    """Fix 'response is possibly unbound' in permission matrix tests"""
    print("\n=== Fixing permission matrix unbound errors ===")

    files = [
        "test_permission_matrix_company_management.py",
        "test_permission_matrix_interview_management.py",
        "test_permission_matrix_resume_access.py",
        "test_permission_matrix_todo_management.py",
    ]

    for filename in files:
        filepath = BACKEND_DIR / "app" / "tests" / filename

        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = []

        for i, line in enumerate(lines):
            # Add response = None before try blocks
            if line.strip() == "try:":
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + "response = None")

            new_lines.append(line)

        content = "\n".join(new_lines)
        filepath.write_text(content, encoding="utf-8")
        print(f"  ✓ Fixed {filename}")

def fix_mbti_endpoints():
    """Fix mbti endpoints BaseException error"""
    print("\n=== Fixing mbti endpoints ===")

    filepath = BACKEND_DIR / "app" / "tests" / "test_mbti_endpoints.py"

    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")

    # Find the line with except Exception and replace with proper exception type
    # Or remove return_exceptions=True from gather call
    content = re.sub(
        r'(asyncio\.gather\([^)]+), return_exceptions=True\)',
        r'\1)',
        content
    )

    filepath.write_text(content, encoding="utf-8")
    print(f"  ✓ Fixed test_mbti_endpoints.py")

def fix_user_management():
    """Fix user management test type error"""
    print("\n=== Fixing user management test ===")

    filepath = BACKEND_DIR / "app" / "tests" / "test_permission_matrix_user_management.py"

    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")

    # Find line 620 area and fix the type mismatch
    # This is a dict subscript issue where value should be list[int] not str
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Look for suspicious assignment like update_data["something"] = "Test"
        # where it should be a list
        if '"Test"' in line and "[" in line and "]" in line:
            # This needs manual inspection - skip for now
            pass

    # Will need to see the actual code
    print(f"  - Skipped test_permission_matrix_user_management.py (needs manual fix)")

def main():
    print("=" * 70)
    print("Fixing remaining test errors without type: ignore")
    print("=" * 70)

    fix_interviews()
    fix_video_calls()
    fix_recruitment_workflow_models()
    fix_permission_matrix_unbound()
    fix_mbti_endpoints()
    fix_user_management()

    print("\n" + "=" * 70)
    print("Done! Run 'npx pyright app/tests' to verify")
    print("=" * 70)

if __name__ == "__main__":
    main()
