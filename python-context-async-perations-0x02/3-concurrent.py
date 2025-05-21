import asyncio
import aiosqlite

DB_NAME = "example.db"

async def async_fetch_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            print("All users:")
            for row in rows:
                print(row)

async def async_fetch_older_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            rows = await cursor.fetchall()
            print("Users older than 40:")
            for row in rows:
                print(row)

async def fetch_concurrently():
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# Optional: Setup example DB (run once to populate)
async def setup_database():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DROP TABLE IF EXISTS users")
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        await db.executemany("INSERT INTO users (name, age) VALUES (?, ?)", [
            ("Alice", 22),
            ("Bob", 30),
            ("Charlie", 45),
            ("Diana", 52),
            ("Ethan", 39)
        ])
        await db.commit()

# Run setup and fetch concurrently
async def main():
    await setup_database()
    await fetch_concurrently()

asyncio.run(main())
