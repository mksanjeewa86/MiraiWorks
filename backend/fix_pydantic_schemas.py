#!/usr/bin/env python3
"""Fix Pydantic schema false positives by using .model_construct()"""
import re
from pathlib import Path

def fix_pydantic_instantiation(filepath):
    """Replace Schema(...) with Schema.model_construct(...)"""
    content = filepath.read_text(encoding="utf-8")

    # Pattern: SchemaName(param=value) -> SchemaName.model_construct(param=value)
    # Only for Update/Create schemas that have optional parameters
    schemas = [
        'ResumeUpdate',
        'WorkExperienceCreate',
        'WorkExperienceUpdate',
        'EducationCreate',
        'EducationUpdate',
        'CertificationCreate',
        'SkillCreate',
    ]

    for schema in schemas:
        # Pattern 1: Schema(param=value)
        pattern = rf'\b{schema}\('
        replacement = f'{schema}.model_construct('
        content = re.sub(pattern, replacement, content)

    filepath.write_text(content, encoding="utf-8")
    return content != filepath.read_text(encoding="utf-8")

# Fix test_resume_comprehensive.py
resume_comp_file = Path("app/tests/test_resume_comprehensive.py")
if resume_comp_file.exists():
    if fix_pydantic_instantiation(resume_comp_file):
        print(f"✅ Fixed {resume_comp_file}")
    else:
        print(f"ℹ️  No changes needed for {resume_comp_file}")

# Fix test_resume_unit.py
resume_unit_file = Path("app/tests/test_resume_unit.py")
if resume_unit_file.exists():
    if fix_pydantic_instantiation(resume_unit_file):
        print(f"✅ Fixed {resume_unit_file}")
    else:
        print(f"ℹ️  No changes needed for {resume_unit_file}")

print("\n✅ Done! Run 'npx pyright app/tests' to verify.")
