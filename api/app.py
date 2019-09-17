from flask import Flask, session, request
from flask_restful import Resource, Api
from flask_cors import CORS

from api.database.Database import Database

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

    for i in range(number_of_pieces * 2):
        if i % 2 == 0:
            board[i] = 1

    for i in range(number_of_pieces * 2):
        if i % 2 == 0:
            board[-i-1] = -1

    return board


def arr_to_str(arr: list) -> str:
    string = ''
    for i in arr:
        string = string + str(i)
    return string


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
                return {'status': False, 'message':'user alredy exist'}
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
            board_size = 2

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


# class GetRoom(Resource):


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


api.add_resource(Session, '/api/session')
api.add_resource(Signup, '/api/session/signup')
api.add_resource(Login, '/api/session/login')
api.add_resource(Logout, '/api/session/logout')

api.add_resource(Room, '/api/room')
api.add_resource(EnterRoom, '/api/room/enter')
# api.add_resource(GetRoom, '/api/room/get')

api.add_resource(SendMessage, '/api/chat/send')
api.add_resource(GetMessage, '/api/chat')


if __name__ == '__main__':
    app.run()
