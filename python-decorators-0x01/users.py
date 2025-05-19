import sqlite3
import csv

conn = sqlite3.connect("example.db")


cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, age TEXT)")

with open("users.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute("SELECT name FROM users WHERE name = ?", (row['name'],))
        results = cursor.fetchone()
        if not results:
            cursor.execute("INSERT INTO users (name, email, age) values(?, ?, ?)", (row['name'], row['email'], row['age']))
    

conn.commit()
conn.close()

