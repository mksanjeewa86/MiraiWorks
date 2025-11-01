#!/usr/bin/env python3
"""Bulk fix remaining errors"""
import re
from pathlib import Path

def fix_file(filepath, pattern, replacement, count=-1):
    """Fix pattern in file"""
    if not filepath.exists():
        return False
    content = filepath.read_text(encoding="utf-8")
    new_content = re.sub(pattern, replacement, content, count=count, flags=re.MULTILINE | re.DOTALL)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False

# Fix all permission matrix response unbound errors
for fname in ["test_permission_matrix_interview_management.py", "test_permission_matrix_resume_access.py", "test_permission_matrix_todo_management.py"]:
    filepath = Path(f"app/tests/{fname}")
    # Add else clause to if/elif chains before assert response
    fix_file(filepath,
        r'(elif method == "DELETE":\s+response = await client\.delete\([^\)]+\))\n(\s+)(assert response)',
        r'\1\n\2else:\n\2    raise ValueError(f"Unsupported method: {method}")\n\2\3',
        count=99)

# Fix recruitment scenario/workflows company_id
for fname in ["test_recruitment_scenario.py", "test_recruitment_workflows.py"]:
    filepath = Path(f"app/tests/{fname}")
    # Add assertion before company_id usage
    fix_file(filepath,
        r'(company_id = test_employer_user\.company_id)\n(\s+)(position = await position_service\.create_position)',
        r'\1\n\2assert company_id is not None\n\2\3')
    fix_file(filepath,
        r'(company_id = test_company\.id)\n(\s+)(position = await position_service\.create_position)',
        r'\1\n\2assert company_id is not None\n\2\3')
    fix_file(filepath,
        r'(employer_company_id=test_employer_user\.company_id)',
        r'employer_company_id=(lambda x: (assert x is not None, x)[1])(test_employer_user.company_id)')
    # Simpler: just add assertion before call
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []
    for i, line in enumerate(lines):
        if "test_employer_user.company_id" in line and "employer_company_id=" in line:
            indent = len(line) - len(line.lstrip())
            new_lines.append(" " * indent + "assert test_employer_user.company_id is not None")
        new_lines.append(line)
    filepath.write_text("\n".join(new_lines), encoding="utf-8")

# Fix recruitment workflow models subscript
filepath = Path("app/tests/test_recruitment_workflow_models.py")
fix_file(filepath,
    r'(workflow_data = response\.json\(\))\n(\s+)(assert workflow_data\[)',
    r'\1\n\2assert workflow_data is not None\n\2\3')

# Fix mbti endpoints BaseException
filepath = Path("app/tests/test_mbti_endpoints.py")
fix_file(filepath,
    r'return_exceptions=True',
    r'return_exceptions=False')

print("Bulk fixes complete!")
