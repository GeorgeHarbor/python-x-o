from flask import session, redirect, url_for
from flask_socketio import emit
from .storage import games


def check_user():
    if 'username' not in session:
        # flash('You must be logged in to create a room.', 'danger')
        return redirect(url_for('main.login'))


def handle_game_log_insert(msg, room):
    games[room]['logs'].append(msg)
    print(games[room]['logs'])
    emit('log', {'msg': games[room]['logs']}, to=room)
