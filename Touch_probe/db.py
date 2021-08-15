import pymysql as mysql
import sys
import time

class DB:
    def __init__(self, hi):
        self.hi = hi

    def get_date(self):
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def connect(self):
        try:
            self.conn = mysql.connect(
                host =  'localhost',
                user= "root",
                password="1234",
                database="MINIAS"
            )
            self.cur = self.conn.cursor()

        except:
            print(f"Error connecting to MariaDB Platform:")
            sys.exit(1)

    def insert_result(self, serial: str, axis: list, result: bool, operator: str):
        self.connect()
        try:
            sql = f'INSERT INTO archive values ({serial}, {axis[0]}, {axis[1]}, {axis[2]}, {axis[3]}, {result}, {self.get_date()}, {operator})'
            # self.hi.status_bar.setText(sql)
            self.cur.execute(sql)
        except Exception as e:
            # self.hi.status_bar.setText(f'[Error] DB insertion {e}')
            print(e)
        
        self.conn.close()


    def get_preset(self):
        self.connect()
        try:
            sql = 'SELECT operator FROM operators'
            ops = self.cur.execute(sql)

            sql = 'SELECT code FROM codes'
            cds = self.cur.execute(sql)

            print(ops)
            print(cds)
        except Exception as e:
            # self.hi.status_bar.setText(f'[Error] DB preset {e}')
            print(e)

        self.conn.close()
        # return [ops, cds]


if __name__ == '__main__':
    db = DB(None)
    db.get_preset()
    db.insert_result(12, [1,2,3,4], True, 'me')