# app.py
from flask import Flask, jsonify, request, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = "secret123"  # for session simulation

users = {}
logged_in_users = set()  # simple session store (usernames)

@app.route('/')
def home():
    return "welcome from flask fundamental 4"

# /greet?name=Kyaw
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    return f"Hello, {name}!"

# JSON user creation with validation
# '{"username": "kyaw", "age": 32 }'
@app.route('/api/userinfo', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    age = data.get('age')

    if not username or not age:
        return jsonify({"error": "missing username or age"}), 400

    try:
        age = int(age)
        if age <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "age must be a positive integer"}), 400

    users[username] = {"username": username, "age": age}
    return jsonify(users[username]), 201

# Pagination support for all users
@app.route('/api/users', methods=['GET'])
def get_all_users():
    limit = request.args.get('limit', default=5, type=int)
    offset = request.args.get('offset', default=0, type=int)
    user_list = list(users.values())
    paginated = user_list[offset:offset+limit]
    return jsonify({
        "total": len(user_list),
        "limit": limit,
        "offset": offset,
        "users": paginated
    })

# Simple login simulation (POST form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        if username in users:
            logged_in_users.add(username)
            return redirect(url_for('hello_user', username=username))
        else:
            msg = "User not found"
    return render_template('login.html', message=msg)

@app.route('/postdata', methods=['POST'])
def post_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    # For example, just echo the received data back
    return jsonify({"received": data}), 200


# HTML form to create user
# {username: kyaw, age: 32}
@app.route('/create_user', methods=['GET', 'POST'])
def create_user_form():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        try:
            age_val = int(age)
            if age_val <= 0:
                msg = "Age must be positive integer"
            elif not username:
                msg = "Username is required"
            else:
                users[username] = {"username": username, "age": age_val}
                return redirect(url_for('users_html'))
        except:
            msg = "Invalid age"
    return render_template('create_user.html', message=msg)

@app.route('/users')
def users_html():
    return render_template('users.html', users=users)

@app.route('/hello/<username>')
def hello_user(username):
    if username in logged_in_users:
        return render_template('hello.html', username=username)
    return "Please login first", 401

if __name__ == "__main__":
    app.run(debug=True)
