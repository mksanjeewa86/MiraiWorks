#!/usr/bin/env python3
"""Fix ALL remaining errors comprehensively"""
import re
from pathlib import Path

def add_assertions_for_none_access(filepath):
    """Add assert not None before accessing attributes on potentially None objects"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        new_lines.append(line)

        # If we see: variable_name = await ...get...() or .json()
        if "= await" in line and ("get_" in line or "get(" in line):
            var_name = line.split("=")[0].strip()
            # Check if next lines access attributes on this variable
            for j in range(i+1, min(i+10, len(lines))):
                if f"{var_name}." in lines[j] and "assert" not in lines[j]:
                    # Add assertion after assignment
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(" " * indent + f"assert {var_name} is not None")
                    break

        # For response.json() calls
        if ".json()" in line and "=" in line:
            var_name = line.split("=")[0].strip()
            # Check if next line accesses this
            if i + 1 < len(lines) and ("[" in lines[i+1] or "len(" in lines[i+1]):
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + f"assert {var_name} is not None")

    filepath.write_text("\n".join(new_lines), encoding="utf-8")
    return True

def fix_string_none_to_string(filepath):
    """Add assertions before using str | None as str"""
    content = filepath.read_text(encoding="utf-8")

    # Pattern: using .share_token or .slug that could be None
    # Add assertion before the line
    lines = content.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        # Check if using a potentially None attribute
        if "share_token" in line or "slug" in line or "public_slug" in line:
            if "assert" not in line:
                # Look backwards for variable assignment
                for j in range(i-1, max(0, i-10), -1):
                    if ".share_token" in lines[j] or ".slug" in lines[j] or ".public_slug" in lines[j]:
                        var_match = re.search(r'(\w+)\.(share_token|slug|public_slug)', lines[j])
                        if var_match:
                            var_name = var_match.group(1)
                            attr_name = var_match.group(2)
                            indent = len(line) - len(line.lstrip())
                            new_lines.insert(-1, " " * indent + f"assert {var_name}.{attr_name} is not None")
                            break

        new_lines.append(line)

    filepath.write_text("\n".join(new_lines), encoding="utf-8")
    return True

# Fix test_resume_comprehensive.py
resume_file = Path("app/tests/test_resume_comprehensive.py")
if resume_file.exists():
    add_assertions_for_none_access(resume_file)
    fix_string_none_to_string(resume_file)
    print("Fixed test_resume_comprehensive.py")

# Fix workflow/meeting files for missing attributes (these are CRUD method issues - skip for now)

# Fix test_video_calls Optional subscript
video_file = Path("app/tests/test_video_calls.py")
if video_file.exists():
    add_assertions_for_none_access(video_file)
    print("Fixed test_video_calls.py")

# Fix test_permission_matrix_user_management.py type mismatch
user_mgmt_file = Path("app/tests/test_permission_matrix_user_management.py")
if user_mgmt_file.exists():
    content = user_mgmt_file.read_text(encoding="utf-8")
    # Line 620 has wrong type - need to see context
    # Skip for now
    print("Skipped test_permission_matrix_user_management.py (manual fix needed)")

print("\nDone! Run 'npx pyright app/tests' to verify remaining errors")
