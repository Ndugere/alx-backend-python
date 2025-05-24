import time
import sqlite3
import functools

# Global cache dictionary
query_cache = {}

def with_db_connection(func):
    """
    Decorator that automatically handles database connection.
    Opens a connection before the function executes and closes it after.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with the connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an error occurs
            conn.close()
    
    return wrapper

def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    Avoids redundant database calls by returning cached results.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Extract the query from arguments
        query = None
        
        # Check if query is in args
        if args:
            query = args[0]
        # Check if query is in kwargs
        elif 'query' in kwargs:
            query = kwargs['query']
        
        # If query is found and already cached, return cached result
        if query and query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]
        
        # Execute the function to get fresh results
        print(f"Executing query and caching result: {query}")
        result = func(conn, *args, **kwargs)
        
        # Cache the result if we have a query
        if query:
            query_cache[query] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print("First call result:", users)

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print("Second call result:", users_again)