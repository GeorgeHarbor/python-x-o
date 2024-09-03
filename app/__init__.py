from flask import Flask
from .main import socketio, main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = 'mojkljuc'

    # Register the main blueprint
    app.register_blueprint(main_blueprint)

    # Initialize SocketIO with the Flask app
    socketio.init_app(app)

    # Initialize the database within the app context
    with app.app_context():
        from .main.db import init_db
        init_db()

    return app
