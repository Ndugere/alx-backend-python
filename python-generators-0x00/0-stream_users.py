#!/usr/bin/python3
"""
Module to stream user data from a MySQL database using a generator.
"""
import mysql.connector
from mysql.connector import Error


def stream_users():
    """
    Generator function that fetches rows one by one from the user_data table.
    Yields each row as a dictionary with the user's information.
    
    Returns:
        Generator yielding dictionaries with user data:
        {
            'user_id': str,
            'name': str,
            'email': str,
            'age': int
        }
    """
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Replace with your actual MySQL password
            database="ALX_prodev"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Execute query to fetch all users
            cursor.execute("SELECT * FROM user_data")
            
            # Yield each row one by one
            for row in cursor:
                yield {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'email': row['email'],
                    'age': row['age']
                }
            
            # Close the cursor and connection
            cursor.close()
            connection.close()
    
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        yield None  # Yield None in case of error to avoid breaking the generator


if __name__ == "__main__":
    # Test the generator
    for i, user in enumerate(stream_users()):
        print(user)
        # Print only first 5 users for testing
        if i >= 4:
            break