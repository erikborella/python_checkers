from flask import Flask
from database.Database import Database

app = Flask(__name__)

@app.route('/')
def hello_world():
    Database()
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
