from flask import Blueprint
from flask_socketio import SocketIO

# Instantiate the SocketIO object correctly
socketio = SocketIO()

# Create the blueprint
main = Blueprint('main', __name__)

# Import routes to register them with the blueprint
from . import routes, events
