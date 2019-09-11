import pymysql
import sys


class Database:

    def __init__(self):

        host = "127.0.0.1"
        user = "root"
        password = "password"
        db = "db"

        self.con = pymysql.connect(host=host, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor)

        sqls = self.parse_sql('database/sql.sql')

        with self.con.cursor() as cursor:
            for sql in sqls:
                cursor.execute(sql)

    def parse_sql(self, filename):
        data = open(filename, 'r').readlines()
        stmts = []
        DELIMITER = ';'
        stmt = ''

        for _, line in enumerate(data):
            if not line.strip():
                continue

            if line.startswith('--'):
                continue

            if 'DELIMITER' in line:
                DELIMITER = line.split()[1]
                continue

            if (DELIMITER not in line):
                stmt += line.replace(DELIMITER, ';')
                continue

            if stmt:
                stmt += line
                stmts.append(stmt.strip())
                stmt = ''
            else:
                stmts.append(line.strip())
        return stmts
