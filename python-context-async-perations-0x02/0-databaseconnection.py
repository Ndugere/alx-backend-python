import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

# Optional: Setup test data
def setup_database():
    with DatabaseConnection("example.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie')")
        conn.commit()

# Required: Perform query and print results
def query_users():
    with DatabaseConnection("example.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        for row in results:
            print(row)

# Run the full workflow
setup_database()
query_users()
