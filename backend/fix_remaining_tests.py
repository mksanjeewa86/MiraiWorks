#!/usr/bin/env python3
"""
Fix remaining test errors systematically without type: ignore
"""
import re
import subprocess
from pathlib import Path

def run_pyright():
    """Run pyright and get errors"""
    result = subprocess.run(
        ["npx", "pyright", "app/tests"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    return result.stdout + result.stderr


def fix_optional_subscript_errors():
    """Fix 'Object of type "None" is not subscriptable' errors"""
    files_to_fix = {
        "test_recruitment_workflow_models.py": [(554, "workflow_data"), (559, "workflow_data")],
        "test_video_calls.py": [
            (44, "call_data"),
            (56, "call_data"),
            (142, "transcription_data"),
            (150, "transcription_data"),
            (157, "transcription_data"),
        ],
    }

    for filename, line_vars in files_to_fix.items():
        filepath = Path(__file__).parent / "app" / "tests" / filename
        if not filepath.exists():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Work backwards to preserve line numbers
        for line_num, var_name in reversed(sorted(line_vars)):
            # Insert assertion before the line
            indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
            assertion = " " * indent + f"assert {var_name} is not None\n"
            # Find the line where var_name was assigned
            for i in range(line_num - 2, max(0, line_num - 20), -1):
                if f"{var_name} =" in lines[i]:
                    lines.insert(i + 1, assertion)
                    break

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"Fixed {filename}")


def fix_company_id_none_errors():
    """Fix 'int | None cannot be assigned to int' for company_id"""
    files = [
        "test_interviews.py",
        "test_interviews_comprehensive.py",
        "test_recruitment_scenario.py",
        "test_recruitment_workflows.py",
    ]

    for filename in files:
        filepath = Path(__file__).parent / "app" / "tests" / filename
        if not filepath.exists():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Add assertions after company_id assignment
        # Pattern: company_id = test_employer_user.company_id or test_company.id
        content = re.sub(
            r'(\s+)(company_id = test_employer_user\.company_id)\n',
            r'\1\2\n\1assert company_id is not None\n',
            content
        )

        content = re.sub(
            r'(\s+)(company_id = test_company\.id)\n',
            r'\1\2\n\1assert company_id is not None\n',
            content
        )

        # For direct usage in function calls, wrap with assertion
        # This is more complex, so let's handle it case by case
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Fixed {filename}")


def fix_optional_member_access():
    """Fix 'is not a known attribute of None' errors"""
    files_patterns = {
        "test_interviews.py": [
            (r'(interview)\.title', r'assert \1 is not None\n        \1.title'),
            (r'(interview)\.status', r'assert \1 is not None\n        \1.status'),
        ],
        "test_activation_comprehensive.py": [
            (r'(user)\.is_active', r'assert \1 is not None\n        \1.is_active'),
            (r'(user)\.last_login', r'assert \1 is not None\n        \1.last_login'),
            (r'(user)\.hashed_password', r'assert \1 is not None\n        \1.hashed_password'),
            (r'(user)\.phone', r'assert \1 is not None\n        \1.phone'),
        ],
    }

    for filename, patterns in files_patterns.items():
        filepath = Path(__file__).parent / "app" / "tests" / filename
        if not filepath.exists():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)

            # Check if line matches any pattern
            for pattern, replacement in patterns:
                if re.search(pattern, line):
                    # Add assertion before this line
                    indent = len(line) - len(line.lstrip())
                    var_match = re.search(r'(\w+)\.\w+', line)
                    if var_match:
                        var_name = var_match.group(1)
                        assertion = " " * indent + f"assert {var_name} is not None\n"
                        # Check if we already added it
                        if i > 0 and assertion.strip() not in new_lines[-2]:
                            new_lines.insert(-1, assertion)
                    break

            i += 1

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"Fixed {filename}")


def fix_response_unbound_errors():
    """Fix 'response is possibly unbound' errors"""
    files = [
        "test_permission_matrix_company_management.py",
        "test_permission_matrix_interview_management.py",
        "test_permission_matrix_resume_access.py",
        "test_permission_matrix_todo_management.py",
    ]

    for filename in files:
        filepath = Path(__file__).parent / "app" / "tests" / filename
        if not filepath.exists():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for i, line in enumerate(lines):
            # Initialize response = None before try blocks
            if line.strip().startswith("try:"):
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + "response = None\n")

            new_lines.append(line)

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"Fixed {filename}")


def main():
    print("Fixing remaining test errors...")
    print("=" * 60)

    print("\n1. Fixing optional subscript errors...")
    fix_optional_subscript_errors()

    print("\n2. Fixing company_id None errors...")
    fix_company_id_none_errors()

    print("\n3. Fixing optional member access errors...")
    fix_optional_member_access()

    print("\n4. Fixing response unbound errors...")
    fix_response_unbound_errors()

    print("\n" + "=" * 60)
    print("Running pyright to check remaining errors...")
    output = run_pyright()
    # Get last line with error count
    for line in output.split("\n"):
        if "errors," in line:
            print(line)

    print("\nDone!")


if __name__ == "__main__":
    main()
