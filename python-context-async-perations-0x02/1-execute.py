import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection = None
        self.results = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        cursor = self.connection.cursor()
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

# Setup for demonstration
def setup_database():
    with sqlite3.connect("example.db") as conn:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS users")
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        c.executemany("INSERT INTO users (name, age) VALUES (?, ?)", [
            ("Alice", 22),
            ("Bob", 30),
            ("Charlie", 27),
            ("Diana", 19)
        ])
        conn.commit()

# Usage of ExecuteQuery
def run_query():
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    with ExecuteQuery("example.db", query, params) as results:
        for row in results:
            print(row)

# Run it
setup_database()
run_query()
