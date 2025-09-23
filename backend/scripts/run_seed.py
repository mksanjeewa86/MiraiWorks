#!/usr/bin/env python3
"""
Simple script runner for seeding exam data.
Usage: python scripts/run_seed.py
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import the seed script
from scripts.seed_exam_data import main

if __name__ == "__main__":
    print("🚀 Starting exam data seeding...")
    print("Make sure your database is running and configured correctly.")
    print("-" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"❌ Failed to seed data: {e}")
        sys.exit(1)
    
    print("-" * 50)
    print("✅ Seeding completed!")
    print("\nYou can now:")
    print("  • Log in as an admin to view the created exams")
    print("  • Test the exam taking interface")
    print("  • View exam statistics and results")