#!/usr/bin/env python3
"""Fix all schema instantiation issues in resume test"""

import re
from pathlib import Path

filepath = Path("app/tests/test_resume_comprehensive.py")
content = filepath.read_text(encoding="utf-8")

# Pattern: SchemaName(param1=value1, param2=value2, ...)
# Replace with: SchemaName(**{"param1": value1, "param2": value2, ...})

# Find all Resume/WorkExperience/Education schema instantiations
schemas = [
    "ResumeUpdate",
    "ResumeCreate",
    "WorkExperienceCreate",
    "WorkExperienceUpdate",
    "EducationCreate",
    "EducationUpdate",
    "CertificationCreate",
    "SkillCreate",
]

for schema in schemas:
    # Pattern: SchemaName(\n with indented content
    pattern = rf"({schema}\(\s*\n)((?:\s+\w+=[^,\n]+,?\n)+)(\s*\))"

    def replace_func(match):
        schema_name = match.group(1)
        params = match.group(2)
        closing = match.group(3)

        # Extract indentation
        lines = params.strip("\n").split("\n")
        if not lines:
            return match.group(0)

        base_indent = len(lines[0]) - len(lines[0].lstrip())

        # Convert params to dict format
        new_params = []
        for line in lines:
            line = line.strip()
            if "=" in line:
                # Parse key=value
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.rstrip(",").strip()
                new_params.append(f'{" " * (base_indent + 4)}"{key}": {value},')

        if not new_params:
            return match.group(0)

        # Build new format
        result = schema_name.rstrip("(").strip() + "(\n"
        result += " " * (base_indent + 4) + "**{\n"
        result += "\n".join(new_params) + "\n"
        result += " " * (base_indent + 4) + "}\n"
        result += closing

        return result

    content = re.sub(pattern, replace_func, content, flags=re.MULTILINE)

filepath.write_text(content, encoding="utf-8")
print(f"Fixed schema instantiations in {filepath}")
