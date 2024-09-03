from . import socketio
from flask_socketio import join_room, emit
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
    current_player = session.get('player_marker')
    username = session.get('username')
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
        conn.execute("UPDATE user SET wins = wins + 1 WHERE username = ?", (winner,))
        conn.commit()

    emit('on_win', {'msg': f"{winner} has won"}, to=room)



@socketio.on('connect')
def handle_connect():
    # Example: Check if the user is authenticated
    if 'username' in session:
        username = session['username']
        marker = session['player_marker']
        room = session.get('room')
        print(f'{username} connected')
        
        # Emit a message back to the client to confirm connection
        emit('connect_response', {'username': username, 'marker': marker, 'room': room})
    else:
        # If the user is not authenticated, disconnect the client
        print('Unauthenticated connection attempt, disconnecting...')
        handle_disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    # Handle any cleanup or logging when the user disconnects
    print('Client disconnected')
