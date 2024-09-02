from flask import Flask
from flask_socketio import SocketIO


socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'mojkljuc'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)

    with app.app_context():
        from app.main.db import init_db
        init_db()

    return app


