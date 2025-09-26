"""
MiraiWorks Database Seeding

Main entry point for database seeding with Docker support.
This script can create database and tables if they don't exist.

USAGE:
    cd backend
    PYTHONPATH=. python app/seeds/seed_data.py

    Or from Docker:
    docker-compose exec backend python app/seeds/seed_data.py
"""

import asyncio
import os

# Set environment to avoid conflicts
os.environ.setdefault("ENVIRONMENT", "development")

# Import the comprehensive seed function
from app.seeds.comprehensive_seed import main as comprehensive_main


async def main():
    """Main entry point - uses comprehensive seeding with all tables."""
    await comprehensive_main()


if __name__ == "__main__":
    asyncio.run(main())
