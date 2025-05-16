#!/usr/bin/python3
"""
Module for batch processing user data from a MySQL database using generators.
This implementation uses yield keyword to create generators (not return statements).
"""
import mysql.connector
from mysql.connector import Error


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows in batches from the user_data table.
    Uses yield to create a generator - no return statements.
    
    Args:
        batch_size (int): Number of records to fetch in each batch
    
    Yields:
        list: A batch of user dictionaries
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
            
            # Initialize offset
            offset = 0
            
            while True:
                # Fetch a batch of records
                query = f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}"
                cursor.execute(query)
                
                # Get all rows in the current batch
                batch = cursor.fetchall()
                
                # Break if no more records
                if not batch:
                    break
                
                # Yield the batch (using yield keyword, not return)
                yield batch
                
                # Update offset for next batch
                offset += batch_size
            
            # Close cursor and connection
            cursor.close()
            connection.close()
    
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")


def batch_processing(batch_size):
    """
    Processes batches of user data and filters users over the age of 25.
    Uses a generator from stream_users_in_batches.
    
    Args:
        batch_size (int): Number of records to process in each batch
    """
    # Get batches from the stream_users_in_batches generator
    for batch in stream_users_in_batches(batch_size):
        # Process each user in the batch
        for user in batch:
            # Filter users over the age of 25
            if user['age'] > 25:
                # Print user information with formatting
                print(f"{{\n    'user_id': '{user['user_id']}', \n    'name': '{user['name']}', \n    'email': '{user['email']}', \n    'age': {user['age']}\n}}\n")


if __name__ == "__main__":
    # Test the batch processing with a small batch size
    batch_processing(10)