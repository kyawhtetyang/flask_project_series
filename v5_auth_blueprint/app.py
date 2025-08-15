# app.py
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from auth import auth_bp
from data import users

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return "Welcome from Flask Fundamental 5"

@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    return f"Hello, {name}!"

# API: Create user
@app.route('/api/userinfo', methods=['POST'])
def create_user_api():
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
    users[username] = {"username": username, "age": age, "password_hash": pw_hash}
    return jsonify({"username": username, "age": age}), 201

# API: Get user
@app.route('/api/userinfo/<username>', methods=['GET'])
def get_user(username):
    user = users.get(username)
    if user:
        return jsonify({"username": user["username"], "age": user["age"]})
    return jsonify({"error": "user not found"}), 404

# HTML: Users list
@app.route('/users')
def users_html():
    return render_template('users.html', users=users)

# HTML: Hello after login
@app.route('/hello/<username>')
def hello_user(username):
    if session.get('username') == username:
        return render_template('hello.html', username=username)
    return redirect(url_for('auth.login'))  # ⬅ FIX changed from 'login' to 'auth.login'

# HTML: Create user form
@app.route('/create_user', methods=['GET', 'POST'])
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
        users[username] = {"username": username, "age": age_int, "password_hash": pw_hash}
        flash("User created successfully. Please login.", "success")
        return redirect(url_for('auth.login'))  # ⬅ FIX changed from 'login' to 'auth.login'

    return render_template('create_user.html')

if __name__ == "__main__":
    app.run(debug=True)