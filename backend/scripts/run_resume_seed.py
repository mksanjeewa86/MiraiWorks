#!/usr/bin/env python3
"""
Simple script runner for seeding resume data.
Usage: python scripts/run_resume_seed.py
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import the seed script
from scripts.seed_resume_data import main

if __name__ == "__main__":
    print("🚀 Starting resume data seeding...")
    print("Make sure your database is running and configured correctly.")
    print("-" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"❌ Failed to seed resume data: {e}")
        sys.exit(1)
    
    print("-" * 50)
    print("✅ Resume seeding completed!")
    print("\nYou can now:")
    print("  • Create and edit resumes via the API")
    print("  • Generate PDFs in Japanese formats")
    print("  • Share resumes publicly")
    print("  • Send resumes via email")
    print("  • Attach resumes to messages")