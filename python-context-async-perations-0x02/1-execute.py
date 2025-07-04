#!/usr/bin/python3
"""
Reusable Query Context Manager

A class-based context manager for executing database queries with
automatic connection and query execution management.
"""

import sqlite3
from typing import Optional, Any, List


class ExecuteQuery:
    """
    A reusable context manager for executing database queries.
    
    Handles database connection, query execution, and resource cleanup
    automatically while returning query results.
    """
    
    def __init__(self, db_path: str, query: str, *params: Any):
        """
        Initialize the query execution context manager.
        
        Args:
            db_path: Path to the database file
            query: SQL query to execute
            *params: Parameters for the SQL query
        """
        self.db_path = db_path
        self.query = query
        self.params = params
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.results: List[Any] = []

    def __enter__(self) -> List[Any]:
        """
        Enter the context manager, establish connection and execute query.
        
        Returns:
            List[Any]: Results of the executed query
            
        Raises:
            sqlite3.Error: If database connection or query execution fails
        """
        try:
            print(f"Opening connection to {self.db_path}")
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()

            print(f"Executing query: {self.query}")
            if self.params:
                print(f"With parameters: {self.params}")
                self.cursor.execute(self.query, self.params)
            else:
                self.cursor.execute(self.query)

            self.results = self.cursor.fetchall()
            print(f"Query executed successfully, {len(self.results)} rows returned")

            return self.results
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise

    def __exit__(self, 
                 exc_type: Optional[type], 
                 exc_val: Optional[Exception], 
                 exc_tb: Optional[object]
            ) -> bool:
        """
        Exit the context manager and cleanup resources.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred  
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            bool: False to propagate exceptions
        """
        try:
            if self.cursor:
                self.cursor.close()

            if self.connection:
                if exc_type is None:
                    self.connection.commit()
                    print("Transaction committed successfully")
                else:
                    self.connection.rollback()
                    print("Transaction rolled back due to error")
                
                self.connection.close()
                print(f"Connection to {self.db_path} closed")

        except sqlite3.Error as e:
            print(f"Error during cleanup: {e}")

        return False  # Propagate any exceptions
    

if __name__ == "__main__":
    with ExecuteQuery("users.db", "SELECT * FROM users WHERE age > ?", 25) as results:
        print("\nQuery Results:")

        if results:
            for row in results:
                print(row)
        else:
            print("No users found matching the criteria")