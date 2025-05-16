#!/usr/bin/python3
"""
Module for memory-efficient aggregation using generators.
Calculates average age from the user database without loading entire dataset into memory.
"""
import mysql.connector
from mysql.connector import Error


def stream_user_ages():
    """
    Generator function that yields user ages one by one from the database.
    Uses yield to provide ages without loading all data into memory at once.
    
    Yields:
        int: Age of each user, one at a time
    """
    try:
        # Import the seed module for database connection
        seed = __import__('seed')
        
        # Connect to the database
        connection = seed.connect_to_prodev()
        
        if connection:
            cursor = connection.cursor()
            
            # Execute query to fetch only the age column
            cursor.execute("SELECT age FROM user_data")
            
            # Yield each age one by one
            for (age,) in cursor:
                yield age
            
            # Close resources
            cursor.close()
            connection.close()
    
    except Error as e:
        print(f"Error streaming ages: {e}")


def calculate_average_age():
    """
    Calculates the average age of users using the stream_user_ages generator.
    Memory-efficient as it only holds running total and count, not all ages.
    
    Returns:
        float: The average age of all users
    """
    total_age = 0
    count = 0
    
    # Use the generator to stream ages one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Calculate average (avoid division by zero)
    if count > 0:
        return total_age / count
    else:
        return 0


if __name__ == "__main__":
    # Calculate and print the average age
    avg_age = calculate_average_age()
    print(f"Average age of users: {avg_age:.2f}")