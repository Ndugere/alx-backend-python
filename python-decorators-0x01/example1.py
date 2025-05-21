import sqlite3
import time

def connect_to_database():
    return sqlite3.connect("example.db")

def generate_results(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

    for result in results:
        yield result
def display_results():
    conn = connect_to_database()
    counter = 1
    start = time.time()
    for result in generate_results(conn):
        print(f"{result[1]} : {result[2]}")
        counter += 1
    conn.close()

    end = time.time()

    print(f"Execution time: {end - start:.4f} seconds to display {counter} data")

display_results()