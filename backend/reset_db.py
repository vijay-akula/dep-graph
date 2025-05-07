# 📁 backend/reset_db.py
import asyncio
from graph_utils import engine, metadata, init_db

async def reset_database():
    async with engine.begin() as conn:
        print("Dropping existing tables...")
        await conn.run_sync(metadata.drop_all)
        print("Creating tables and populating initial data...")
        await conn.run_sync(metadata.create_all)
    await init_db()
    print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
