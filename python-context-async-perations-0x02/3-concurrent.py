import asyncio
import aiosqlite

DB_NAME = "example.db"

async def async_fetch_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return rows  # ✅ Return the full result set

async def async_fetch_older_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            rows = await cursor.fetchall()
            return rows  # ✅ Return the full result set

async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    print("All users:")
    for user in all_users:
        print(user)

    print("\nUsers older than 40:")
    for user in older_users:
        print(user)

# Optional: Setup database with data
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

# Run the full flow
async def main():
    await setup_database()
    await fetch_concurrently()

asyncio.run(main())
