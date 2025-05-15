from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM user_data")
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            for row in batch:
                yield row
    finally:
        cursor.close()
        connection.close()


def batch_processing(batch_size):
    result = []
    for user in stream_users_in_batches(batch_size):
        if user['age'] > 25:
            result.append(user)
    return result
