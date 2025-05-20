import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Opening database connection...")
        conn = sqlite3.connect("example.db")
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
            print("Database connection closed.")
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# ✅ Call the function
user = get_user_by_id(user_id=1)
print(user)
