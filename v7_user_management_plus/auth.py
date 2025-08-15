# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash
from data import users
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# ==========================
# Config session timeout
# ==========================
SESSION_TIMEOUT_MINUTES = 30

@auth_bp.before_app_request
def make_session_permanent():
    """
    Set session lifetime only if session is permanent.
    """
    current_app.permanent_session_lifetime = timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    if session.get('permanent'):
        session.permanent = True
    else:
        session.permanent = False

# ==========================
# Login Route
# ==========================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember')  # checkbox

        user = users.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            session['role'] = user.get('role', 'user')

            if remember_me == 'on':
                session.permanent = True
                session['permanent'] = True
            else:
                session.permanent = False
                session['permanent'] = False

            flash(f"Logged in as {username}", "success")
            return redirect(url_for('users.hello_user', username=username))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

# ==========================
# Logout Route
# ==========================
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return render_template('logout.html')