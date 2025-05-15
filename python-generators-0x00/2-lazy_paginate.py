import mysql.connector
from seed import connect_to_prodev


def paginate_users(page_size, offset):
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (page_size, offset))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def lazy_paginate(page_size):
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        for user in page:
            yield user
        offset += page_size
