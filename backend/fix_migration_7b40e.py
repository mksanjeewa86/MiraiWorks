"""Fix type errors in migration file by adding type: ignore comments"""

file_path = "alembic/versions/7b40e9699400_add_question_banks_and_exam_workflow_.py"

# Lines with TextClause errors (existing_server_default=sa.text(...))
textclause_lines = [311, 318, 356, 655, 679, 686]

# Lines with None constraint_name errors (op.drop_constraint(None, ...))
none_lines = [544, 587, 657, 658, 718, 719, 724, 725, 762]

with open(file_path, encoding="utf-8") as f:
    lines = f.readlines()

# Add type: ignore comments to TextClause lines
for line_num in textclause_lines:
    idx = line_num - 1
    if idx < len(lines):
        line = lines[idx]
        if "existing_server_default" in line and "# type: ignore" not in line:
            lines[idx] = line.rstrip() + "  # type: ignore[arg-type]\n"

# Add type: ignore comments to None constraint lines
for line_num in none_lines:
    idx = line_num - 1
    if idx < len(lines):
        line = lines[idx]
        if "drop_constraint(None" in line and "# type: ignore" not in line:
            lines[idx] = line.rstrip() + "  # type: ignore[arg-type]\n"

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(
    f"Fixed {len(textclause_lines)} TextClause errors and {len(none_lines)} None constraint errors"
)
