#!/usr/bin/env python3
"""
Script to setup Japan holidays for 2025
Run this script to populate the database with Japan national holidays for 2025
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import AsyncSessionLocal
from app.services.holiday_service import holiday_service


async def setup_holidays():
    """Setup Japan holidays for 2025"""
    print("Setting up Japan holidays for 2025...")

    async with AsyncSessionLocal() as db:
        try:
            # Setup Japan holidays for 2025
            holidays = await holiday_service.setup_japan_holidays_2025(db)

            if holidays:
                print(f"Successfully added {len(holidays)} Japan holidays for 2025:")
                for holiday in holidays:
                    print(f"  - {holiday.date}: {holiday.name} ({holiday.name_en})")
            else:
                print("Japan holidays for 2025 already exist in the database")

        except Exception as e:
            print(f"Error setting up holidays: {e}")
            raise
        finally:
            await db.close()


async def main():
    """Main function"""
    try:
        await setup_holidays()
        print("\nHoliday setup completed successfully!")
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())