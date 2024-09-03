from . import socketio
from flask_socketio import join_room, emit, leave_room
from flask import session
from .utils import handle_game_log_insert
from .db import get_db_connection
from .storage import games

@socketio.on('join_room_event')
def handle_join_room_event():
    room = session.get('room')
    username = session.get('username')
    marker = session.get('player_marker')
    join_room(room)
    print(f'Handling join_room_event for {username} in room {room} ' )

    handle_game_log_insert(f'{username} has joined the room as {marker}', room)
    print(f'Emitting log event to room {room}')

@socketio.on('move')
def on_move(data):
    room = session.get('room')
    current_player = None
    username = session.get('username')

    for players in games[room]['players']:
        if players['username'] == username:
            current_player = players['marker']
            break

    next_player = 'O' if current_player == 'X' else 'X'

    handle_game_log_insert(f'{username} has moved to index {data["index"]}', room)

    emit('move', {'index': data['index'], 'player_marker': current_player, 'next_player': next_player}, to=room)


@socketio.on('win')
def handle_win(data):
    room = data['room']
    if games[room]['winner'] is not None:
        return

    winner = None
    players = games[room]['players']
    for player in players:
        if player['marker'] == data['winner']:
            winner = player['username']
            break

    games[room]['winner'] = winner
    with get_db_connection() as conn:
        conn.execute("UPDATE user SET wins = wins + 2 WHERE username = ?", (winner,))
        conn.commit()

    emit('on_win', {'msg': f"{winner} has won"}, to=room)


@socketio.on('draw')
def handle_draw(data):
    room = data.get('room')
    players = games[room]['players']

    usernames = [player['username'] for player in players]

    if len(usernames) == 0:
        return

    with get_db_connection() as conn:
        conn.execute("UPDATE user SET wins = wins + 1 WHERE username in (?, ?)", (usernames[0], usernames[1],))
        conn.commit()


@socketio.on('leave')
def on_leave(data):
    username = session.get('username')
    room = data['room']
    leave_room(room)
    emit('player_left', {'msg': f'{username} has left the room.'}, to=room)

@socketio.on('reset')
def on_reset(data):
    room = data['room']
    games[room]['winner'] = None

    for player in games[room]['players']:
        player['marker'] = 'X' if player['marker'] == 'O' else 'O'

    games[room]['logs'] = []

    emit('on_reset', {'msg': 'The game has been reset.'}, to=room)


@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        username = session['username']
        marker = session['player_marker']
        room = session.get('room')
        print(f'{username} connected')
        
        emit('connect_response', {'username': username, 'marker': marker, 'room': room})
