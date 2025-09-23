#!/usr/bin/env python3
"""
Setup script for MBTI functionality
Runs migration and seeds the database with MBTI questions
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import get_session
from app.seeds.mbti_questions_seed import MBTI_QUESTIONS_SEED
from app.models.mbti_test import MBTIQuestion
from sqlalchemy import select


async def setup_mbti():
    """Setup MBTI tables and seed data"""
    print("🧠 Setting up MBTI personality test system...")
    
    try:
        async with get_session() as db:
            # Check if questions already exist
            existing = await db.execute(select(MBTIQuestion).limit(1))
            if existing.scalar():
                print("✅ MBTI questions already exist!")
                return
            
            print(f"📚 Seeding {len(MBTI_QUESTIONS_SEED)} MBTI questions...")
            
            # Insert all questions
            for i, q_data in enumerate(MBTI_QUESTIONS_SEED, 1):
                question = MBTIQuestion(
                    question_number=q_data["question_number"],
                    dimension=q_data["dimension"],
                    question_text_en=q_data["question_text_en"],
                    question_text_ja=q_data["question_text_ja"],
                    option_a_en=q_data["option_a_en"],
                    option_a_ja=q_data["option_a_ja"],
                    option_b_en=q_data["option_b_en"],
                    option_b_ja=q_data["option_b_ja"],
                    scoring_key=q_data["scoring_key"],
                    is_active=True
                )
                db.add(question)
                
                # Show progress
                if i % 10 == 0:
                    print(f"  Added {i}/{len(MBTI_QUESTIONS_SEED)} questions...")
            
            await db.commit()
            print("✅ Successfully seeded all MBTI questions!")
            print("🎉 MBTI system is ready to use!")
            
    except Exception as e:
        print(f"❌ Error setting up MBTI system: {e}")
        raise


def main():
    """Main setup function"""
    print("🚀 MBTI Setup Script")
    print("=" * 50)
    
    try:
        asyncio.run(setup_mbti())
        print("\n🎯 Setup completed successfully!")
        print("You can now use the MBTI personality test feature.")
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()