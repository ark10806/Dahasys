import mysql
import sys

try:
    conn = mysql.connect(
        user= "root",
        password="1234",
        host="127.0.0.1",
        port=3306,
        database="MINIAS"
    )

except mysql.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

cur.execute(
    "INSERT"
)

class DB:
    def __init__(self):
        pass

    def connect(self):
        try:
            self.conn = mysql.connect(
                user= "root",
                password="1234",
                host="127.0.0.1",
                port=3306,
                database="MINIAS"
            )

        except mysql.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def insert_result(self, serial, axis, result, date, operator):
        cur = conn.cursor()

        self.connect()
        cur.execute(
            f'INSERT INTO archive values ({serial}, {axis[0]}, {axis[1]}, {axis[2]}, {axis[3]},\
                {result}, {date}, {operator})'
        )
        self.conn.disconnect()
