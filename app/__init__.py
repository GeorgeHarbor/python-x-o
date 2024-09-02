from flask import Flask
from .routes import main as main_blueprint

import sqlite3

from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'mojkljuc'

    app.register_blueprint(main_blueprint)

    socketio.init_app(app)

    with app.app_context():
        init_db()

    return app


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                wins INTEGER DEFAULT 0 
            )'''
        )
        conn.commit()
