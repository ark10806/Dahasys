import pymysql as mar

conn = None
try:
    conn = mar.connect(
        host =      'localhost',
        user =      'root',
        password =  '1234',
        database =  'MINIAS'
    )
except Exception as e:
    print(f'[ERR]: DB connection failed\n \t{e}')
    exit()
cur = conn.cursor()

sql = 'DROP TABLE IF EXISTS archive'
cur.execute(sql)
sql = 'CREATE TABLE archive(serial INT NOT NULL PRIMARY KEY, axis1 NUMERIC(2,2), axis2 NUMERIC(2,2), axis3 NUMERIC(2,2), axis4 NUMERIC(2,2), result BOOLEAN, date VARCHAR(10), operator VARCHAR(10))'
cur.execute(sql)

sql = 'DROP TABLE IF EXISTS operators'
cur.execute(sql)
sql = 'CREATE TABLE operators(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, operator VARCHAR(10))'
cur.execute(sql)
sql = 'INSERT INTO operators VALUES(0, "ML LEE")'
cur.execute(sql)
sql = 'INSERT INTO operators VALUES(0, "YS CHO")'
cur.execute(sql)

sql = 'DROP TABLE IF EXISTS codes'
cur.execute(sql)
sql = 'CREATE TABLE codes(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, code VARCHAR(20))'
cur.execute(sql)
sql = 'INSERT INTO codes VALUES(0, "SC301111")'
cur.execute(sql)
sql = 'INSERT INTO codes VALUES(0, "SC301112")'
cur.execute(sql)

conn.close()
