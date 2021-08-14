import mysql
import sys
import time

class DB:
    def __init__(self):
        pass

    def get_date(self):
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def connect(self):
        try:
            self.conn = mysql.connect(
                user= "root",
                password="1234",
                host="127.0.0.1",
                port=3306,
                database="MINIAS"
            )

        except:
            print(f"Error connecting to MariaDB Platform:")
            sys.exit(1)

    def insert_result(self, serial: str, axis: list, result: str, operator: str, hi: str):
        sql = f'INSERT INTO archive values ({serial}, {axis[0]}, {axis[1]}, {axis[2]}, {axis[3]}, {result}, {self.get_date()}, {operator})'
        print(sql)
        hi.status_bar.setText(sql)
        # self.connect()


        # cur = self.conn.cursor()
        # cur.execute(
        #     f'INSERT INTO archive values ({serial}, {axis[0]}, {axis[1]}, {axis[2]}, {axis[3]},\
        #         {result}, {date}, {operator})'
        # )
        # self.conn.disconnect()

