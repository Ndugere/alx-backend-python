import mysql.connector 
import csv
import os

# Function to connect to the MySQL server (no database yet)
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="984529b169bb.d05f4c1b.alx-cod.online",
            port=34118,                                   
            user="984529b169bb",                        
            password="46d55fa791845166d59e"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}!")
        return None

# Function to connect specifically to the ALX_prodev database
def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="984529b169bb.d05f4c1b.alx-cod.online",
            port=34118,
            user="984529b169bb",
            password="46d55fa791845166d59e",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to create the database
def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error Creating a database: {err}")

# Function to create the table
def create_table(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5, 2) NOT NULL
            )
        """)
      
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON user_data(user_id)")
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

# Function to insert data from a CSV file
def insert_data(connection, csv_file_path):
    try:
        cursor = connection.cursor()
        with open(csv_file_path, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
               
                cursor.execute("SELECT name FROM user_data WHERE user_id = %s", (row["user_id"],))
                result = cursor.fetchone()
                if not result:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s ,%s)
                    """, (
                        row['user_id'], 
                        row['name'], 
                        row['email'], 
                        row['age']
                    ))
        connection.commit()
        cursor.close()
        print("Data inserted successfully")
    except FileNotFoundError:
        print(f"CSV file '{csv_file_path}' not found.")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
