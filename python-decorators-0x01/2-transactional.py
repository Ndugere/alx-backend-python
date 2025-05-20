import sqlite3 
import functools

# ✅ Decorator to handle database connection
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Opening database connection")
        conn = sqlite3.connect("example.db")
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
            print("Closing database connection")
    return wrapper

# ✅ Decorator to handle transaction (commit or rollback)
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            print("Transaction committed")
            return result
        except Exception as e:
            conn.rollback()
            print("Transaction rolled back due to error:", e)
            raise  # re-raise the exception for visibility
    return wrapper

# ✅ Function that updates user email, wrapped in both decorators
@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

# ✅ Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
