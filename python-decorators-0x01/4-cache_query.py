import time
import sqlite3 
import functools

# ✅ Global dictionary to store cached results
query_cache = {}

# ✅ Decorator to handle database connection
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Opening database connection")
        conn = sqlite3.connect("example.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
            print("Closing database connection")
    return wrapper

# ✅ Decorator to cache query results
def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get('query') or (args[0] if args else None)
        if query in query_cache:
            print("[CACHE] Returning cached result for query.")
            return query_cache[query]
        
        print("[DB] Query not cached. Executing and caching result.")
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

# ✅ Function using cache_query and with_db_connection decorators
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# ✅ First call will execute and cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# ✅ Second call will return the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
