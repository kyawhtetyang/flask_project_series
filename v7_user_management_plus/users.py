from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from data import users
import os
import time

users_bp = Blueprint('users', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ===== Helper Functions =====
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

def role_required(roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for('users.users_html'))
            return f(*args, **kwargs)
        return decorated
    return decorator

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_pic(file, username):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{username}_{int(time.time())}.{ext}"
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
        file.save(upload_path)
        return filename
    return None

# ===== Web Routes =====
@users_bp.route('/users')
@login_required
def users_html():
    query = request.args.get('q', '').lower()
    filtered_users = {u: info for u, info in users.items() if query in u.lower()} if query else users
    return render_template('users.html', users=filtered_users, query=query)

@users_bp.route('/users/search')
@login_required
def search_users():
    query = request.args.get('q', '').lower()
    filtered_users = {u: info for u, info in users.items() if query in u.lower()} if query else {}
    return render_template('search_results.html', users=filtered_users)

@users_bp.route('/users/profile/<username>')
@login_required
def profile(username):
    user = users.get(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('users.users_html'))

    # Only admin or the user themselves can view
    if session.get('role') != 'admin' and session.get('username') != username:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('users.users_html'))

    return render_template('profile.html', user=user)

@users_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user_form():
    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        password = request.form.get('password')
        email = request.form.get('email')
        bio = request.form.get('bio')
        file = request.files.get('profile_pic')

        if not username or not age or not password:
            flash("Username, age, and password are required.", "danger")
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

        profile_pic_filename = save_profile_pic(file, username) if file else None

        pw_hash = generate_password_hash(password)
        users[username] = {
            "username": username,
            "age": age_int,
            "password_hash": pw_hash,
            "role": "user",
            "email": email or "",
            "bio": bio or "",
            "profile_pic": profile_pic_filename
        }
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
        email = request.form.get('email')
        bio = request.form.get('bio')
        file = request.files.get('profile_pic')

        try:
            age_int = int(age)
            if age_int <= 0:
                raise ValueError
        except:
            flash("Age must be a positive integer.", "danger")
            return render_template('edit_user.html', user=user)

        if password or password_confirm:
            if password != password_confirm:
                flash("Passwords do not match.", "danger")
                return render_template('edit_user.html', user=user)
            user['password_hash'] = generate_password_hash(password)

        user['age'] = age_int
        user['email'] = email or ""
        user['bio'] = bio or ""

        if file:
            profile_pic_filename = save_profile_pic(file, username)
            if profile_pic_filename:
                user['profile_pic'] = profile_pic_filename

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

@users_bp.route('/hello/<username>')
@login_required
def hello_user(username):
    return render_template('hello.html', username=username)

# ===== API Routes =====
@users_bp.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.get_json()
    username = data.get('username')
    age = data.get('age')
    password = data.get('password')

    if not username or not age or not password:
        return jsonify({"error": "username, age, and password required"}), 400

    try:
        age = int(age)
        if age <= 0:
            raise ValueError
    except:
        return jsonify({"error": "age must be a positive integer"}), 400

    if username in users:
        return jsonify({"error": "username already exists"}), 400

    pw_hash = generate_password_hash(password)
    users[username] = {
        "username": username,
        "age": age,
        "password_hash": pw_hash,
        "role": "user",
        "email": "",
        "bio": "",
        "profile_pic": None
    }
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
