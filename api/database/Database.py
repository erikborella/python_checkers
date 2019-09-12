import pymysql


class Database(object):

    def __init__(self):

        host = "127.0.0.1"
        user = "root"
        password = "password"
        db = "db"

        self.con = pymysql.connect(host=host, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor)

        sqls = self.parse_sql('api/database/sql.sql')

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

    def create_user(self, username, password, icon):
        sql = "INSERT INTO user(username, password, wins, loses, draws, icon) VALUES (%s, %s, %s, %s, %s, %s)"
        with self.con.cursor() as cursor:
            cursor.execute(sql, (username, password, 0, 0, 0, icon))
            id = cursor.lastrowid
        self.con.commit()
        return id

    def get_users(self):
        sql = "SELECT * FROM user"
        with self.con.cursor() as cursor:
            cursor.execute(sql)
            users = cursor.fetchall()
        return users

    def get_user(self, username, password):
        sql = "SELECT * FROM user WHERE username = %s and password = %s"
        with self.con.cursor() as cursor:
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
        return user

    def get_user_by_id(self, id):
        sql = "SELECT id, username, wins, loses, draws, icon FROM user WHERE id=%s"
        with self.con.cursor() as cursor:
            cursor.execute(sql, id)
            user = cursor.fetchone()
        return user