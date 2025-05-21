import sqlite3
from contextlib import contextmanager

@contextmanager
def database_connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()

# Setup sample database and insert test data
def setup():
    with database_connection("example.db") as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        c.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie')")
        conn.commit()

# Run query
def query():
    with database_connection("example.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        for row in c.fetchall():
            print(row)

setup()
query()
