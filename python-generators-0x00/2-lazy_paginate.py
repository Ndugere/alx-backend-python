#!/usr/bin/python3
"""
Module for lazy pagination of user data using generators.
This implementation uses yield to create generators for efficient pagination.
"""
import mysql.connector
from mysql.connector import Error


def paginate_users(page_size, offset):
    """
    Function to fetch paginated user data from the database.
    
    Args:
        page_size (int): Number of records per page
        offset (int): Starting position for fetching records
        
    Returns:
        list: A list of user dictionaries for the requested page
    """
    try:
        # Import the seed module for database connection
        seed = __import__('seed')
        
        # Connect to the database
        connection = seed.connect_to_prodev()
        
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Execute query with pagination
            cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
            
            # Fetch all rows for this page
            rows = cursor.fetchall()
            
            # Close resources
            cursor.close()
            connection.close()
            
            return rows
            
    except Error as e:
        print(f"Error fetching paginated data: {e}")
        return []


def lazy_pagination(page_size):
    """
    Generator function that implements lazy loading of paginated data.
    Uses yield to return each page only when needed.
    
    Args:
        page_size (int): Number of records per page
        
    Yields:
        list: A page of user data (list of dictionaries)
    """
    # Initialize offset at 0
    offset = 0
    
    # Keep fetching pages until we get an empty page
    while True:
        # Fetch the current page using paginate_users
        current_page = paginate_users(page_size, offset)
        
        # If the page is empty, we've reached the end of the data
        if not current_page:
            break
        
        # Yield the current page (using yield keyword, not return)
        yield current_page
        
        # Update offset for the next page
        offset += page_size


if __name__ == "__main__":
    # Test the lazy pagination
    for i, page in enumerate(lazy_pagination(10)):
        print(f"Page {i+1}:")
        for user in page:
            print(f"  {user['name']} ({user['email']})")
        
        # Only show first 3 pages for testing
        if i >= 2:
            break