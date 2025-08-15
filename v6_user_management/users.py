# users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from data import users

users_bp = Blueprint('users', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash("Login required.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('users.users_html'))
        return f(*args, **kwargs)
    return decorated

@users_bp.route('/hello/<username>')
@login_required
def hello_user(username):
    if session.get('username') == username:
        return render_template('hello.html', username=username)
    else:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('auth.login'))

@users_bp.route('/users')
@login_required
def users_html():
    return render_template('users.html', users=users)

@users_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user_form():
    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        password = request.form.get('password')

        if not username or not age or not password:
            flash("All fields are required.", "danger")
            return render_template('create_user.html')

        try:
            age_int = int(age)
            if age_int <= 0:
                raise ValueError
        except:
            flash("Age must be a positive integer.", "danger")
            return render_template('create_user.html')

        if username in users:
            flash("Username already exists.", "danger")
            return render_template('create_user.html')

        pw_hash = generate_password_hash(password)
        users[username] = {"username": username, "age": age_int, "password_hash": pw_hash, "role": "user"}
        flash("User created successfully.", "success")
        return redirect(url_for('users.users_html'))

    return render_template('create_user.html')

@users_bp.route('/users/edit/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(username):
    user = users.get(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('users.users_html'))

    if request.method == 'POST':
        age = request.form.get('age')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        try:
            age_int = int(age)
            if age_int <= 0:
                raise ValueError
        except:
            flash("Age must be a positive integer.", "danger")
            return render_template('edit_user.html', user=user)

        if not password or not password_confirm:
            flash("Password and confirmation required.", "danger")
            return render_template('edit_user.html', user=user)

        if password != password_confirm:
            flash("Passwords do not match.", "danger")
            return render_template('edit_user.html', user=user)

        pw_hash = generate_password_hash(password)
        user['age'] = age_int
        user['password_hash'] = pw_hash
        flash(f"User '{username}' updated successfully.", "success")
        return redirect(url_for('users.users_html'))

    return render_template('edit_user.html', user=user)

@users_bp.route('/users/delete/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user(username):
    user = users.get(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('users.users_html'))

    if request.method == 'POST':
        users.pop(username)
        flash(f"User '{username}' deleted successfully.", "success")
        return redirect(url_for('users.users_html'))

    return render_template('confirm_delete.html', user=user)

# API routes with full CRUD for users

@users_bp.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.get_json()
    username = data.get('username')
    age = data.get('age')
    password = data.get('password')

    if not username or not age or not password:
        return jsonify({"error": "username, age and password required"}), 400

    try:
        age = int(age)
        if age <= 0:
            raise ValueError
    except:
        return jsonify({"error": "age must be positive integer"}), 400

    if username in users:
        return jsonify({"error": "username already exists"}), 400

    pw_hash = generate_password_hash(password)
    users[username] = {"username": username, "age": age, "password_hash": pw_hash, "role": "user"}
    return jsonify({"username": username, "age": age}), 201

@users_bp.route('/api/users/<username>', methods=['GET', 'PUT', 'DELETE'])
def api_user_detail(username):
    user = users.get(username)
    if not user:
        return jsonify({"error": "user not found"}), 404

    if request.method == 'GET':
        return jsonify({"username": user["username"], "age": user["age"]})

    if request.method == 'PUT':
        data = request.get_json()
        age = data.get('age')
        password = data.get('password')

        if not age or not password:
            return jsonify({"error": "age and password required"}), 400

        try:
            age_int = int(age)
            if age_int <= 0:
                raise ValueError
        except:
            return jsonify({"error": "age must be positive integer"}), 400

        pw_hash = generate_password_hash(password)
        user['age'] = age_int
        user['password_hash'] = pw_hash
        return jsonify({"username": user["username"], "age": user["age"]})

    if request.method == 'DELETE':
        users.pop(username)
        return jsonify({"message": "user deleted"}), 200

