#!/usr/bin/env python3
"""Fix all real pyright errors (not Pydantic false positives)"""
import re
from pathlib import Path

def fix_optional_member_access(filepath, line_num, var_name, attr_name):
    """Add assertion before accessing attribute on potentially None object"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the line and add assertion before it
    if line_num - 1 < len(lines):
        target_line = lines[line_num - 1]
        indent = len(target_line) - len(target_line.lstrip())

        # Add assertion on line before
        assertion = " " * indent + f"assert {var_name} is not None"

        # Check if assertion already exists
        if line_num - 2 >= 0 and assertion.strip() in lines[line_num - 2]:
            return False  # Already fixed

        lines.insert(line_num - 1, assertion)
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return True
    return False

def fix_optional_subscript(filepath, line_num, var_name):
    """Add assertion before subscripting potentially None object"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    if line_num - 1 < len(lines):
        target_line = lines[line_num - 1]
        indent = len(target_line) - len(target_line.lstrip())
        assertion = " " * indent + f"assert {var_name} is not None"

        if line_num - 2 >= 0 and assertion.strip() in lines[line_num - 2]:
            return False

        lines.insert(line_num - 1, assertion)
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return True
    return False

def fix_str_none_to_str(filepath, line_num, var_name, attr_name):
    """Add assertion before using str | None as str"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    if line_num - 1 < len(lines):
        target_line = lines[line_num - 1]
        indent = len(target_line) - len(target_line.lstrip())
        assertion = " " * indent + f"assert {var_name}.{attr_name} is not None"

        if line_num - 2 >= 0 and assertion.strip() in lines[line_num - 2]:
            return False

        lines.insert(line_num - 1, assertion)
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return True
    return False

def add_else_to_if_elif(filepath, line_num):
    """Add else clause to if/elif chain to prevent 'possibly unbound'"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the elif/if block and add else
    if line_num - 1 < len(lines):
        # Look backward to find the if/elif chain
        for i in range(line_num - 2, max(0, line_num - 20), -1):
            if 'elif method == "DELETE"' in lines[i]:
                # Add else after this elif
                indent = len(lines[i]) - len(lines[i].lstrip())

                # Find the end of this elif block
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(" " * (indent + 4)):
                        # This is the next line after elif block
                        else_clause = [
                            " " * indent + "else:",
                            " " * (indent + 4) + 'raise ValueError(f"Unsupported method: {method}")'
                        ]

                        # Check if already exists
                        if j < len(lines) and "else:" in lines[j]:
                            return False

                        lines[j:j] = else_clause
                        filepath.write_text("\n".join(lines), encoding="utf-8")
                        return True
                break
    return False

def fix_sqlalchemy_where_bool(filepath, line_num):
    """Fix SQLAlchemy where clause with plain bool"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    if line_num - 1 < len(lines):
        line = lines[line_num - 1]
        # Change .where(bool_value) to .where(bool_value == True)  # type: ignore[arg-type]
        if "is_deleted is True" in line:
            lines[line_num - 1] = line.replace("is_deleted is True", "is_deleted == True")
            filepath.write_text("\n".join(lines), encoding="utf-8")
            return True
    return False

# Fix test_resume_comprehensive.py - Optional member access
resume_file = Path("app/tests/test_resume_comprehensive.py")
if resume_file.exists():
    print("Fixing test_resume_comprehensive.py...")

    # Line 340: updated_resume.status
    fix_optional_member_access(resume_file, 340, "updated_resume", "status")

    # Line 347: updated_resume.status
    fix_optional_member_access(resume_file, 347, "updated_resume", "status")

    # Line 373: updated_resume.visibility
    fix_optional_member_access(resume_file, 373, "updated_resume", "visibility")

    # Line 404-406: formatted_resume attributes
    fix_optional_member_access(resume_file, 404, "formatted_resume", "resume_format")
    fix_optional_member_access(resume_file, 405, "formatted_resume", "resume_language")
    fix_optional_member_access(resume_file, 406, "formatted_resume", "furigana_name")

    # Line 457: resume.share_token (str | None to str)
    # Need to look back to find where resume is assigned
    content = resume_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    for i in range(456, max(0, 446), -1):
        if "resume = " in lines[i] and "await" in lines[i]:
            indent = len(lines[457]) - len(lines[457].lstrip())
            lines.insert(457, " " * indent + "assert resume.share_token is not None")
            resume_file.write_text("\n".join(lines), encoding="utf-8")
            break

    # Line 485: resume.public_slug (str | None to str)
    content = resume_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    for i in range(484, max(0, 474), -1):
        if "resume = " in lines[i] and "await" in lines[i]:
            indent = len(lines[485]) - len(lines[485].lstrip())
            lines.insert(485, " " * indent + "assert resume.public_slug is not None")
            resume_file.write_text("\n".join(lines), encoding="utf-8")
            break

    # Line 865-869: complex_resume attributes
    fix_optional_member_access(resume_file, 865, "complex_resume", "status")
    fix_optional_member_access(resume_file, 866, "complex_resume", "is_public")
    fix_optional_member_access(resume_file, 867, "complex_resume", "experiences")
    fix_optional_member_access(resume_file, 868, "complex_resume", "educations")
    fix_optional_member_access(resume_file, 869, "complex_resume", "skills")

    # Line 220-221: len(data.json()) where data could be None
    content = resume_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    if "data.json()" in lines[219]:
        indent = len(lines[219]) - len(lines[219].lstrip())
        lines.insert(219, " " * indent + "assert data is not None")
        resume_file.write_text("\n".join(lines), encoding="utf-8")

    print("Fixed test_resume_comprehensive.py")

# Fix test_recruitment_workflow_models.py - Optional subscript
workflow_models_file = Path("app/tests/test_recruitment_workflow_models.py")
if workflow_models_file.exists():
    print("Fixing test_recruitment_workflow_models.py...")

    # Line 554: workflow[0]
    fix_optional_subscript(workflow_models_file, 554, "workflow")

    # Line 559: workflow[0] (different workflow variable)
    # Need to check context
    content = workflow_models_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    if line_num := 559:
        for i in range(558, max(0, 548), -1):
            if "workflow = " in lines[i]:
                var_match = re.search(r'(\w+)\s*=.*workflow', lines[i])
                if var_match:
                    var_name = var_match.group(1)
                    fix_optional_subscript(workflow_models_file, 559, var_name)
                break

    print("Fixed test_recruitment_workflow_models.py")

# Fix test_permission_matrix_company_management.py - response possibly unbound
company_mgmt_file = Path("app/tests/test_permission_matrix_company_management.py")
if company_mgmt_file.exists():
    print("Fixing test_permission_matrix_company_management.py...")
    add_else_to_if_elif(company_mgmt_file, 482)
    print("Fixed test_permission_matrix_company_management.py")

# Fix test_video_call_crud.py - Optional member access and wrong parameter
video_crud_file = Path("app/tests/test_video_call_crud.py")
if video_crud_file.exists():
    print("Fixing test_video_call_crud.py...")

    # Line 23: enable_transcription -> transcription_enabled
    content = video_crud_file.read_text(encoding="utf-8")
    content = content.replace("enable_transcription=True", "transcription_enabled=True")
    video_crud_file.write_text(content, encoding="utf-8")

    # Line 121: call.replace
    fix_optional_member_access(video_crud_file, 121, "call", "replace")

    # Line 291: call.processing_status
    fix_optional_member_access(video_crud_file, 291, "call", "processing_status")

    # Line 302-304: call attributes
    fix_optional_member_access(video_crud_file, 302, "call", "processing_status")
    fix_optional_member_access(video_crud_file, 303, "call", "transcript_text")
    fix_optional_member_access(video_crud_file, 304, "call", "processed_at")

    print("Fixed test_video_call_crud.py")

# Fix test_video_call_endpoints.py - Optional member access
video_endpoints_file = Path("app/tests/test_video_call_endpoints.py")
if video_endpoints_file.exists():
    print("Fixing test_video_call_endpoints.py...")

    # Line 162: call_data.status
    fix_optional_member_access(video_endpoints_file, 162, "call_data", "status")

    # Line 165: call_data.status
    fix_optional_member_access(video_endpoints_file, 165, "call_data", "status")

    # Line 206: call_data.status
    fix_optional_member_access(video_endpoints_file, 206, "call_data", "status")

    # Line 207: call_data.ended_at
    fix_optional_member_access(video_endpoints_file, 207, "call_data", "ended_at")

    print("Fixed test_video_call_endpoints.py")

# Fix test_todo_attachment_crud.py - missing parameters
todo_attach_file = Path("app/tests/test_todo_attachment_crud.py")
if todo_attach_file.exists():
    print("Fixing test_todo_attachment_crud.py...")

    content = todo_attach_file.read_text(encoding="utf-8")

    # Add description and file_extension parameters
    # Line 234
    content = re.sub(
        r'(TodoAttachmentCreate\([^)]*uploaded_by=user\.id,)',
        r'\1\n            description="Test attachment",\n            file_extension=".txt",',
        content,
        count=1
    )

    # Line 368 and 422 - similar pattern
    content = re.sub(
        r'(TodoAttachmentCreate\([^)]*uploaded_by=\w+\.id,)(\s*\))',
        r'\1\n            description="Test attachment",\n            file_extension=".txt",\2',
        content
    )

    todo_attach_file.write_text(content, encoding="utf-8")
    print("Fixed test_todo_attachment_crud.py")

# Fix test_resumes_endpoints_comprehensive.py - wrong User parameters
resumes_endpoints_file = Path("app/tests/test_resumes_endpoints_comprehensive.py")
if resumes_endpoints_file.exists():
    print("Fixing test_resumes_endpoints_comprehensive.py...")

    content = resumes_endpoints_file.read_text(encoding="utf-8")

    # Line 30: Change full_name -> first_name/last_name, remove password
    # Pattern: User(..., full_name="...", password="...")
    content = re.sub(
        r'User\((.*?)full_name="([^"]+)"(.*?)password="[^"]*"(.*?)\)',
        lambda m: f'User({m.group(1)}first_name="{m.group(2).split()[0]}", last_name="{m.group(2).split()[-1]}"{m.group(3)}{m.group(4)})',
        content
    )

    resumes_endpoints_file.write_text(content, encoding="utf-8")
    print("Fixed test_resumes_endpoints_comprehensive.py")

# Fix test_workflow_relationships.py - SQLAlchemy where clause
workflow_rel_file = Path("app/tests/test_workflow_relationships.py")
if workflow_rel_file.exists():
    print("Fixing test_workflow_relationships.py...")

    # Line 533 and 575: is_deleted is True -> is_deleted == True
    fix_sqlalchemy_where_bool(workflow_rel_file, 533)
    fix_sqlalchemy_where_bool(workflow_rel_file, 575)

    print("Fixed test_workflow_relationships.py")

# Fix test_permission_matrix_user_management.py - wrong type at line 620
user_mgmt_file = Path("app/tests/test_permission_matrix_user_management.py")
if user_mgmt_file.exists():
    print("Fixing test_permission_matrix_user_management.py...")

    content = user_mgmt_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Line 620: headers["X-Test"] = "Test" but headers expects list[int]
    # Need to see context - likely wrong type annotation or wrong usage
    if len(lines) > 619 and '"X-Test"]' in lines[619]:
        # Change to proper type or fix the usage
        # Let's check what headers is
        print("Line 620:", lines[619])
        print("Context:", "\n".join(lines[617:622]))

    print("Checked test_permission_matrix_user_management.py (manual fix needed)")

print("\nAll fixes applied! Run 'npx pyright app/tests' to verify.")
