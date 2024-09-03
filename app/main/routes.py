from flask import session, render_template, redirect, url_for, request, flash
import sqlite3
from flask_socketio import emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from . import main
from .db import get_db_connection
from .utils import check_user
from .storage import games
import uuid




@main.route('/')
def index():
    if 'username' in session:
        users = []
        with get_db_connection() as conn:
            users = conn.execute("SELECT * FROM user  where wins > 0 ORDER BY wins DESC").fetchall()
        return render_template('index.html', username=session['username'], users=users)
    return redirect(url_for('.login'))


'''

User management routes

'''

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['username'] = user['username']
                return redirect(url_for('.index'))
            else:
                flash('Invalid username or password.', 'danger')
                return render_template('login.html')

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        with get_db_connection() as conn:
            try:
                conn.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('.login'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Try a different one.', 'danger')
                return render_template('register.html')
    return render_template('register.html')


@main.route('/logout')
def logout():
    session.pop('username', None)  
    session.pop('room', None)  
    session.pop('player_marker', None)  
    flash('You have been logged out.', 'info')
    return redirect(url_for('.login'))

'''


'''

@main.route('/create_room')
def create_room():
    check_user()
    game_id = str(uuid.uuid4())
    session['room'] = game_id
    session['player_marker'] = 'X'

    games[game_id] = {'players': [{'username': session['username'], 'marker': session['player_marker']}], 'logs': [] }
    print(games)

    return redirect(url_for('.handle_join_room', room=game_id, player_marker=session['player_marker']))

@main.route('/player_join_room', methods = ['POST'])
def player_join_room():
    room_number = request.form.get('room_number')
    session['room'] = room_number
    session['player_marker'] = 'O'
    
    return redirect(url_for('.handle_join_room', room=room_number))


@main.route('/join_room')
def handle_join_room():
    check_user()
    return render_template('room.html', room=session['room'], player_marker=session['player_marker'])

