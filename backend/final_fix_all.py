#!/usr/bin/env python3
"""Final comprehensive fix for all remaining errors"""
from pathlib import Path
import re

def fix_permission_matrix_unbound():
    """Fix response unbound in remaining permission matrix files"""
    for fname in ["test_permission_matrix_interview_management.py",
                  "test_permission_matrix_resume_access.py",
                  "test_permission_matrix_todo_management.py"]:
        filepath = Path(f"app/tests/{fname}")
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for pattern: elif method == "DELETE":
            #                      response = ...
            #                  assert response.status_code
            if 'elif method == "DELETE":' in line:
                new_lines.append(line)
                # Get next few lines
                j = i + 1
                while j < len(lines) and j < i + 10:
                    new_lines.append(lines[j])
                    if 'assert response.status_code' in lines[j]:
                        # Insert else clause before this assert
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        new_lines.insert(-1, " " * indent + "else:")
                        new_lines.insert(-1, " " * (indent + 4) + 'raise ValueError(f"Unsupported method: {method}")')
                        new_lines.insert(-1, "")
                        i = j
                        break
                    j += 1
                    if j == i + 10:
                        i = j - 1
                        break
            else:
                new_lines.append(line)

            i += 1

        filepath.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"Fixed {fname}")

def fix_recruitment_workflow_models():
    """Fix workflow_data subscript errors"""
    filepath = Path("app/tests/test_recruitment_workflow_models.py")
    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")

    # Add assertion after workflow_data = response.json()
    content = re.sub(
        r'(workflow_data = response\.json\(\))\n(\s+)(assert workflow_data\[)',
        r'\1\n\2assert workflow_data is not None\n\2\3',
        content
    )

    filepath.write_text(content, encoding="utf-8")
    print("Fixed test_recruitment_workflow_models.py")

def fix_mbti_endpoints():
    """Fix mbti BaseException error"""
    filepath = Path("app/tests/test_mbti_endpoints.py")
    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")

    # Remove return_exceptions=True from asyncio.gather
    content = re.sub(
        r',\s*return_exceptions=True',
        '',
        content
    )

    filepath.write_text(content, encoding="utf-8")
    print("Fixed test_mbti_endpoints.py")

def fix_video_calls():
    """Fix video call subscript errors"""
    filepath = Path("app/tests/test_video_calls.py")
    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        new_lines.append(line)

        # After response.json() assignments, add assertion
        if "= response.json()" in line and "=" in line:
            var_name = line.split("=")[0].strip()
            indent = len(line) - len(line.lstrip())
            # Check if next line is not already an assertion
            if i + 1 < len(lines) and "assert" not in lines[i + 1]:
                new_lines.append(" " * indent + f"assert {var_name} is not None")

    filepath.write_text("\n".join(new_lines), encoding="utf-8")
    print("Fixed test_video_calls.py")

def main():
    print("Running final comprehensive fixes...")
    print("=" * 60)

    fix_permission_matrix_unbound()
    fix_recruitment_workflow_models()
    fix_mbti_endpoints()
    fix_video_calls()

    print("=" * 60)
    print("Final fixes complete!")

if __name__ == "__main__":
    main()
