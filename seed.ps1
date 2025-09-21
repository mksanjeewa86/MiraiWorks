# Quick Seed Runner - No prompts, just runs the seed script
Set-Location backend
$env:PYTHONPATH = "."
python app\seed_data.py
Set-Location ..