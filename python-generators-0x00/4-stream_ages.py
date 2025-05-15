import mysql.connector
from seed import connect_to_prodev

def stream_user_ages():
    connection = connect_to_prodev()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT age FROM user_data")
        for row in cursor:
            yield row[0]
    finally:
        cursor.close()
        connection.close()


def calculate_average_age():
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1

    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.1f}")
    else:
        print("No users found.")

# Run the function
calculate_average_age()
