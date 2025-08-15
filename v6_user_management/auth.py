# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from data import users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            session['role'] = user.get('role', 'user')  # default role
            flash("Logged in successfully.", "success")
            return redirect(url_for('users.hello_user', username=username))
        else:
            flash("Invalid username or password.", "danger")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return render_template('logout.html')
