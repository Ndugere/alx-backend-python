import sqlite3
import time

def connector_to_database():
    return sqlite3.connect('example.db')

def generate_results(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    
    while True:
        results = cursor.fetchone()
        if results == None:
            break
        yield results


def display_results():
    counter = 1
    conn = connector_to_database()
    start = time.time()
    for each in generate_results(conn):
        print(f"{each[1]} : {each[2]}")
        counter += 1
    end = time.time()
    conn.close()
    print(f"Execution time: {end - start:.4f} seconds to display {counter} data")


display_results()