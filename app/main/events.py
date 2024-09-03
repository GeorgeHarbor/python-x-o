from . import socketio
from flask_socketio import join_room, emit
from flask import session
from .utils import handle_game_log_insert

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
    print(data)
    room = session.get('room')
    current_player = session.get('player_marker')
    next_player = 'O' if current_player == 'X' else 'X'
    
    emit('move', {'index': data['index'], 'player_marker': current_player, 'next_player': next_player}, to=room)



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
