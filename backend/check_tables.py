import asyncio

from sqlalchemy import text

from app.database import get_db


async def check_tables():
    async for db in get_db():
        result = await db.execute(text("SHOW TABLES LIKE '%job%'"))
        tables = [row[0] for row in result.fetchall()]
        print("Job-related tables:", tables)

        result = await db.execute(text("SHOW TABLES"))
        all_tables = [row[0] for row in result.fetchall()]
        print(f"Total tables: {len(all_tables)}")

        # Check for position/jobs related tables
        position_tables = [t for t in all_tables if 'position' in t.lower()]
        print("Position-related tables:", position_tables)
        break

if __name__ == "__main__":
    asyncio.run(check_tables())
