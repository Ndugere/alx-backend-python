import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    def wrapper(*args, **kwargs):
        query = None
        if args:
            query = args[0]
        elif 'query' in kwargs:
            query = kwargs['query']

        # ✅ Log with current date and time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] Executing SQL query: {query}")

        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

users = fetch_all_users(query="SELECT * FROM users")
