#!/usr/bin/python3
"""
Script to set up MySQL database and populate it with sample data.
"""
import mysql.connector
import csv
import os
from mysql.connector import Error


def connect_db():
    """
    Connects to the MySQL database server.
    
    Returns:
        connection: MySQL connection object if successful, None otherwise
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"  # Replace with your actual MySQL password
        )
        
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    
    return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    
    Returns:
        connection: MySQL connection object to ALX_prodev if successful, None otherwise
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Replace with your actual MySQL password
            database="ALX_prodev"
        )
        
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
    
    return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    
    Args:
        connection: MySQL connection object to ALX_prodev
    """
    try:
        cursor = connection.cursor()
        
        # Create table with specified fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5,0) NOT NULL,
                INDEX idx_user_id (user_id)
            )
        """)
        
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):
    """
    Inserts data in the database if it does not exist.
    
    Args:
        connection: MySQL connection object to ALX_prodev
        csv_file: Path to the CSV file containing the data
    """
    try:
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} not found")
            return
        
        cursor = connection.cursor()
        
        # Read data from CSV file
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Skip header row
            
            # Prepare SQL query for inserting data
            sql = """
                INSERT IGNORE INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
            """
            
            # Insert each row into the database
            rows_to_insert = []
            for row in csv_reader:
                if len(row) >= 4:  # Ensure we have all required fields
                    rows_to_insert.append((row[0], row[1], row[2], row[3]))
            
            cursor.executemany(sql, rows_to_insert)
            connection.commit()
            
            print(f"{cursor.rowcount} records inserted successfully")
            
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Test the functions
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        
        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, 'user_data.csv')
            connection.close()