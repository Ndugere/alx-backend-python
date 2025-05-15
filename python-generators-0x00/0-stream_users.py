import mysql.connector
from seed import connect_to_prodev

def stream_users():
    connection = connect_to_prodev()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM user_data")
        for row in cursor:
            yield row
    finally:
        cursor.close()
        connection.close()
