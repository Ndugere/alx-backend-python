#!/usr/bin/python3
"""
Database Connection Context Manager

A class-based context manager for handling SQLite database connections
"""

import sqlite3
from typing import Optional


class DatabaseConnection:
    """
    A context manager for SQLite database connections.
    
    Handles automatic opening and closing of database connections
    with proper resource management and error handling.
    """
    
    def __init__(self, db_path: str = "users.db"):
        """
        Initialize the context manager with database path.
        
        Args:
            db_path: Path to the database file to connect to
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> sqlite3.Cursor:
        """
        Enter the context manager and establish database connection.
        
        Returns:
            sqlite3.Cursor: Database cursor for executing queries
            
        Raises:
            sqlite3.Error: If database connection fails
        """
        print(f"Opening connection to {self.db_path}")
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            
            return self.cursor
        except sqlite3.Error as e:
            print(f"Failed to connect to database: {e}")
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
    with DatabaseConnection("users.db") as cursor:
        cursor.execute("SELECT * FROM users") 
        results = cursor.fetchall()

        print("\nQuery results:")
        for row in results:
            print(row)