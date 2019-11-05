from flask import Flask, session, request
from flask_restful import Resource, Api
from flask_cors import CORS

from database.Database import Database

import math

import hashlib

app = Flask(__name__)
app.secret_key = "MAZZUTTI"
CORS(app, supports_credentials=True)
api = Api(app)


def hash_string(string):
    sha_signature = hashlib.sha256(string.encode()).hexdigest()
    return sha_signature


def check_existent_username(username):
    users = Database().get_users()
    for user in users:
        if user['username'] == username:
            return True
    return False


def send_invalid_form():
    return {'status': False, 'message': 'Invalid Form'}, 400


def send_not_logged():
    return {'status': False, 'message': 'not logged'}


def is_logged():
    return 'logged_in' in session


def get_username_by_id(user_list, id):
    for user in user_list:
        if user['id'] == id:
            return user['username']
    return None


def get_messages(room_id):
    user_list = Database().get_users()
    messages = Database().get_group_message(room_id)
    for message in messages:
        message['username'] = get_username_by_id(user_list, message['user_id'])
    return messages


def create_board(board_size=8):
    board = []
    board_size = int(board_size)

    if board_size % 2 != 0:
        raise Exception("The board size need to be a pair number")

    number_of_pieces = ((board_size ** 2) - (board_size * 2)) / 4
    number_of_pieces = int(number_of_pieces)
    print(number_of_pieces)

    for i in range(board_size ** 2):
        board.append(0)

    i = 0
    last = 1
    counter = -1
    put: bool = True
    while counter <= number_of_pieces:

        if i % board_size == 0 and i != 0:
            board[i] = last
            counter += 1
            i += 1
            continue

        if put:
            board[i] = 1
            counter += 1
            last = 1
            put = False
        else:
            put = True
            last = 0

        i += 1

    i = 0
    last = -1
    counter = -1
    put: bool = True
    while counter <= number_of_pieces:

        if i % board_size == 0 and i != 0:
            board[-i-1] = last
            counter += 1
            i += 1
            continue

        if put:
            board[-i-1] = -1
            counter += 1
            last = -1
            put = False
        else:
            put = True
            last = 0

        i += 1

    return board


def arr_to_str(arr: list) -> str:
    string = ''
    for i in arr:
        if i == -1:
            i = 3
        elif i == -2:
            i = 4

        string = string + str(i)
    return string


def str_to_arr(string: str) -> list:
    arr: list = []
    for char in string:
        if char == '3':
            char = -1
        elif char == '4':
            char = -2
        else:
            char = int(char)
        arr.append(char)

    return arr


def arr_to_matrix(arr: list) -> list:
    row_size = int(math.sqrt(len(arr)))
    matrix: list = []
    counter = 0

    for i in range(row_size):
        pre_arr: list = []
        for j in range(row_size):
            pre_arr.append(arr[counter])
            counter += 1
        matrix.append(pre_arr)

    return matrix


def check_valid_position(row: int, col: int, board: list) -> bool:
    board_size = len(board)

    if row < 0 or row >= board_size:
        return False

    if col < 0 or col >= board_size:
        return False

    return True


def check_valid_movement(row: int, col: int, board: list) -> list:
    movements: list = []
    piece = board[row][col]
    is_dama = True if (board[row][col] ==
                       2 or board[row][col] == -2) else False

    if check_valid_position(row-1, col-1, board):
        if board[row-1][col-1] == 0:
            movements.append({"row": row-1, "col": col-1})
        else:
            if check_valid_position(row-2, col-2, board):
                if board[row-1][col-1] != piece:
                    movements.append({"row": row-2, "col": col-2})

    if check_valid_position(row-1, col+1, board):
        if board[row-1][col-1] == 0:
            movements.append({"row": row-1, "col": col+1})
        else:
            if check_valid_position(row-2, col+2, board):
                if board[row-1][col+1] != piece:
                    movements.append({"row": row-2, "col": col+2})

    if is_dama:
        if check_valid_position(row+1, col-1, board):
            if board[row+1][col-1] == 0:
                movements.append({"row": row+1, "col": col-1})
            else:
                if check_valid_position(row+2, col-2, board):
                    movements.append({"row": row+2, "col": col-2})

        if check_valid_position(row+1, col+1, board):
            if board[row+1][col-1] == 0:
                movements.append({"row": row+1, "col": col+1})
            else:
                if check_valid_position(row+2, col-2, board):
                    movements.append({"row": row+2, "col": col+2})

    return movements


class Session(Resource):

    def get(self):
        if is_logged():
            user = Database().get_user_by_id(session['id'])
            return {'status': True, 'user': user}
        else:
            return send_not_logged()


class Signup(Resource):

    def post(self):
        username = request.form['username']
        password = request.form['password']
        icon = request.form['icon']

        if username and password and icon:
            if not check_existent_username(username):
                password = hash_string(password)
                id = Database().create_user(username, password, icon)
                session['logged_in'] = True
                session['id'] = id
                return {'status': True}
            else:
                return {'status': False, 'message': 'user alredy exist'}
        else:
            return send_invalid_form()


class Login(Resource):

    def post(self):
        username = request.form['username']
        password = request.form['password']

        if username and password:
            password = hash_string(password)
            user = Database().get_user(username, password)
            if user:
                session['logged_in'] = True
                session['id'] = user['id']
                return {'status': True}
            else:
                return {'status': False, 'message': "user not find"}
        else:
            return send_invalid_form()


class Logout(Resource):

    def get(self):
        session.pop('logged_in', None)
        session.pop('id', None)
        return {'status': True}


class Room(Resource):

    def post(self):
        name = request.form['name']
        password = request.form['password']
        board_size = request.form['board_size']

        if not board_size:
            board_size = 8

        if is_logged():
            user_id = session['id']
            if name and password:
                password = hash_string(password)
                board = arr_to_str(create_board(board_size))
                id = Database().create_room(name, password, board, user_id)
                return {'status': True, 'room_id': id}
            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class EnterRoom(Resource):

    def post(self):
        room_id = request.form['room_id']
        password = request.form['password']
        if is_logged():
            user_id = session['id']
            if room_id and password:
                password = hash_string(password)

                status = Database().add_user_in_room(room_id, password, user_id)

                return status
            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class GetRoom(Resource):

    def get(self):
        if is_logged():
            rooms = Database().get_rooms()
            for room in rooms:
                room['board'] = arr_to_matrix(str_to_arr(room['board']))

            return {'status': True, 'rooms': rooms}
        else:
            return send_not_logged()

    def post(self):
        room_id = request.form['room_id']

        if is_logged():
            user_id = session['id']
            if room_id:
                room = Database().get_room(room_id)
                room['board'] = arr_to_matrix(str_to_arr(room['board']))

                # Auto reverse the board for the second player
                if user_id == room['user2_id']:
                    room['board'] = room['board'][::-1]

                del room['password']

                return {'status': True, 'room': room}
            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class DeleteRoom(Resource):

    def post(self):
        room_id = request.form['room_id']

        if is_logged():
            if room_id:
                Database().delete_room(room_id)
                return {'status': True}
            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class SendMessage(Resource):

    def post(self):
        room_id = request.form['room_id']
        message = request.form['message']

        if is_logged():
            user_id = session['id']
            if room_id and message:
                Database().add_message(user_id, room_id, message)
                return {'status': True}
            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class GetMessage(Resource):

    def post(self):
        room_id = request.form['room_id']

        if is_logged():
            if room_id:
                messages = get_messages(room_id)
                return {'status': True, 'messages': messages}
            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class GetPossibleMovements(Resource):

    def post(self):
        row = request.form['row']
        col = request.form['col']
        room_id = request.form['room_id']

        if is_logged():
            user_id = session['id']
            if row and col and room_id:
                row = int(row)
                col = int(col)
                room = Database().get_room(room_id)
                if user_id != room['user1_id'] and user_id != room['user2_id']:
                    return {'status': False, 'message': "you"}

                board: list = arr_to_matrix(str_to_arr(room['board']))

                if user_id == room['user2_id']:
                    board = board[::-1]

                if board[row][col] == 0:
                    return {'status': False, 'message': "You don't select a piece"}

                movements = check_valid_movement(row, col, board)

                session['piece_selected'] = {'col': col, 'row': row}
                session['movements'] = movements

                return {'status': True, 'movements': movements}

            else:
                return send_invalid_form()
        else:
            return send_not_logged()


class Play(Resource):
    def post(self):
        row = request.form['row']
        col = request.form['col']
        room_id = request.form['room_id']

        if is_logged():
            user_id = session['id']
            if row and col and room_id:
                row = int(row)
                col = int(col)
                room = Database().get_room(room_id)
                if user_id != room['user1_id'] and user_id != room['user2_id']:
                    return {'status': False, 'message': "you"}

                board: list = arr_to_matrix(str_to_arr(room['board']))

                if user_id == room['user2_id']:
                    board = board[::-1]
                    if room['turn'] == 1:
                        return {'status': False, 'message': 'Is not your time to move'}

                if not 'piece_selected' in session:
                    return {'status': False, 'message': "You need to select a piece"}

                select_row = int(session['piece_selected']['row'])
                select_col = int(session['piece_selected']['col'])

                moved = False

                for moves in session['movements']:
                    if moves['row'] == row and moves['col'] == col:
                        piece = board[select_row][select_col]
                        board[select_row][select_col] = 0
                        board[row][col] = piece
                        moved = True
                        break

                if moved:
                    room['turn'] = room['turn'] * -1

                room['board'] = board

                print(room)

                return {'status': moved}

            else:
                return send_invalid_form()
        else:
            return send_not_logged()


api.add_resource(Session, '/api/session')
api.add_resource(Signup, '/api/session/signup')
api.add_resource(Login, '/api/session/login')
api.add_resource(Logout, '/api/session/logout')

api.add_resource(Room, '/api/room')
api.add_resource(EnterRoom, '/api/room/enter')
api.add_resource(GetRoom, '/api/room/get')
api.add_resource(DeleteRoom, '/api/room/delete')

api.add_resource(SendMessage, '/api/chat/send')
api.add_resource(GetMessage, '/api/chat')

api.add_resource(GetPossibleMovements, '/api/game/movements')
api.add_resource(Play, '/api/game/play')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
