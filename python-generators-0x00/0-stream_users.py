import mysql.connector

from seed import connect_to_prodev

def stream_users():
   connnection = connect_to_prodev()
   cursor = connnection.cursor()
   cursor.execute("SELECT * FROM user_data")

   for row in rows:
      yield row

   cursor.close()
   connnection.close()