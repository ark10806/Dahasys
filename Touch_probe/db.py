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

    def is_unique(self, serial):
        self.connect()
        try:
            sql = f'SELECT * FROM archive WHERE serial={serial}'
            if self.cur.execute(sql) != 0 :
                return False
        except Exception as e:
            print(f'[err]is_unique: {e}')
            return False
        return True

    def insert_result(self, serial: str, axis: list, result: bool, operator: str):
        self.connect()
        try:
            sql = 'INSERT INTO archive (serial, axis1, axis2, axis3, axis4, result, date, operator) values (%s, %s, %s, %s, %s, %s, %s, %s)'
                
                # {serial}, {axis[0]}, {axis[1]}, {axis[2]}, {axis[3]}, {result}, {self.get_date()}, "{operator}")'
            # print(sql)
            # self.hi.status_bar.setText(sql)
            self.cur.execute(sql, (serial, axis[0], axis[1], axis[2], axis[3], result, self.get_date(), operator))
        except Exception as e:
            # self.hi.status_bar.setText(f'[Error] DB insertion {e}')
            self.hi.show_msg(f"serial {serial}은 중복된 번호입니다. 다시 입력 후 print 버튼을 누르십시오.")
            print(f'ins error: {e}')
        
        self.conn.close()


    def get_preset(self):
        self.connect()
        ops = []
        cds = []
        try:
            sql = 'SELECT operator FROM operators'
            self.cur.execute(sql)
            ops = self.cur.fetchall()

            sql = 'SELECT code FROM codes'
            self.cur.execute(sql)
            cds = self.cur.fetchall()

            print(f'ops: {ops}')
            print(f'cds: {cds}')
        except Exception as e:
            # self.hi.status_bar.setText(f'[Error] DB preset {e}')
            print(f'get err: {e}')

        self.conn.close()
        # return [ops, cds]


if __name__ == '__main__':
    db = DB(None)
    db.get_preset()
    db.insert_result(13, [1.0,2.0,3.1,4.1], True, 'me')