#!/usr/bin/python3
"""
Concurrent Asynchronous Database Queries

Run multiple database queries concurrently using asyncio.gather
and aiosqlite for asynchronous SQLite operations.
"""

import asyncio
import aiosqlite
from typing import List, Tuple, Any


async def async_fetch_users() -> List[Tuple[Any, ...]]:
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        List[Tuple[Any, ...]]: List of all user records
    """
    print("Starting to fetch all users...")

    async with aiosqlite.connect("users.db") as conn:
        async with conn.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print(f"Fetched {len(users)} users")

            return users


async def async_fetch_older_users() -> List[Tuple[Any, ...]]:
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        List[Tuple[Any, ...]]: List of user records where age > 40
    """
    print("Starting to fetch users older than 40...")

    async with aiosqlite.connect("users.db") as conn:
        async with conn.execute("SELECT * FROM users WHERE age > ?", (40, )) as cursor:
            older_users = await cursor.fetchall()
            print(f"Fetched {len(older_users)} users older than 40")

            return older_users


async def fetch_concurrently() -> None:
    """
    Execute both database queries concurrently using asyncio.gather.
    
    This function demonstrates concurrent execution of multiple
    asynchronous database operations.
    """
    print("Starting concurrent database queries...")

    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    if all_users:
        print("\nAll users:")
        for user in all_users:
            print(user)
    else:
        print("\nNo users")

    if older_users:
        print("\nUsers older than 40:")
        for user in older_users:
            print(user)
    else:
        print("\nNo users older than 40 found")


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())