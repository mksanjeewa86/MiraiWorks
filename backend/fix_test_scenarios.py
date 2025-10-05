import re

# Read the file
with open("app/tests/test_recruitment_workflow_scenarios.py", encoding="utf-8") as file:
    content = file.read()

# Fix method signatures to include client and auth_headers fixtures
patterns = [
    (
        r"async def test_recruitment_workflow_candidate_withdrawal\(self\):",
        "async def test_recruitment_workflow_candidate_withdrawal(self, client, auth_headers):",
    ),
    (
        r"async def test_bulk_candidate_assignment_and_processing\(self\):",
        "async def test_bulk_candidate_assignment_and_processing(self, client, auth_headers):",
    ),
    (
        r"async def test_process_modification_with_active_candidates\(self\):",
        "async def test_process_modification_with_active_candidates(self, client, auth_headers):",
    ),
    (
        r"async def test_complex_conditional_workflow\(self\):",
        "async def test_complex_conditional_workflow(self, client, auth_headers):",
    ),
]

# Apply replacements
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Remove AsyncClient context managers that are now redundant
content = re.sub(
    r'\s+async with AsyncClient\(app=app, base_url="http://test"\) as client:\n',
    "",
    content,
)

# Write back to file
with open(
    "app/tests/test_recruitment_workflow_scenarios.py", "w", encoding="utf-8"
) as file:
    file.write(content)

print("Fixed test scenario file")
