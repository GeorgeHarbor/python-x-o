from flask import Blueprint, session, render_template, redirect, url_for
from . import get_db_connection 


main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'username' in session:
        users = []
        with get_db_connection() as conn:
            users = conn.execute("SELECT * FROM user ORDER BY wins DESC").fetchall()
        return render_template('home.html', username=session['username'], users=users)
    return redirect(url_for('login'))
