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

    def create_room(self, name, password, board, user_id):
        sql = "INSERT INTO room(name, password, board, turn, user1_id) VALUES (%s, %s, %s, %s, %s)"
        with self.con.cursor() as cursor:
            cursor.execute(sql, (name, password, board, 1, user_id))
            id = cursor.lastrowid
        self.con.commit()
        return id

    def get_room(self, room_id):
        sql = "SELECT * FROM room WHERE id = %s"
        with self.con.cursor() as cursor:
            cursor.execute(sql, room_id)
            room = cursor.fetchone()
        return room

    def add_user_in_room(self, room_id, room_password, user_id):
        room = self.get_room(room_id)
        print(room)
        if room_id is None:
            if room['password'] == room_password:
                sql = "UPDATE room SET user2_id = %s WHERE id = %s"
                with self.con.cursor() as cursor:
                    cursor.execute(sql, (user_id, room_id))
                self.con.commit()
                return {'status': True}
            else:
                return {'status': False, 'message': 'Password incorect'}
        else:
            return {'status': False, 'message': 'Room not find'}

    def add_message(self, user_id, room_id, message):
        sql = "INSERT INTO message(user_id, room_id, message) VALUES (%s, %s, %s)"
        with self.con.cursor() as cursor:
            cursor.execute(sql, (user_id, room_id,  message))
            id = cursor.lastrowid
        self.con.commit()
        return id

    def get_group_message(self, room_id):
        sql = "SELECT * FROM message WHERE room_id = %s"
        with self.con.cursor() as cursor:
            cursor.execute(sql, room_id)
            rooms = cursor.fetchall()
        return rooms