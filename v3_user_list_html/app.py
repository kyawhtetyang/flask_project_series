# app.py
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

users = {}  # store user data

@app.route('/')
def home():
    return "welcome from flask fundamental 3"

# /greet?name=Kyaw
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    return f"Hello, {name}!"

# {username: kyaw, age: 32}
@app.route('/api/userinfo', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    age = data.get('age')

    if not username or not age:
        return jsonify({"error": "no JSON body found"}), 400

    users[username] = {"username": username, "age": age}
    return jsonify(users[username]), 201

# /api/userinfo/kyaw
@app.route('/api/userinfo/<username>', methods=['GET'])
def get_user(username):
    user = users.get(username)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "user not found"}), 404

# update user
@app.route('/api/userinfo/<username>', methods=['PUT'])
def update_user(username):
    if username not in users:
        return jsonify({"error": "user not found"}), 404
    data = request.get_json()
    age = data.get('age')
    if age:
        users[username]['age'] = age
    return jsonify(users[username])

# delete user
@app.route('/api/userinfo/<username>', methods=['DELETE'])
def delete_user(username):
    if username in users:
        del users[username]
        return jsonify({"message": "user deleted"})
    return jsonify({"error": "user not found"}), 404

# all users JSON
@app.route('/api/users', methods=['GET'])
def get_all_users():
    return jsonify(list(users.values()))

# all users HTML table
@app.route('/users')
def users_html():
    return render_template('users.html', users=users)

# {"msg": "hi"}
@app.route('/postdata', methods=['POST'])
def postdata():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no JSON data received"}), 400
    return jsonify({"you said": data})

# /hello/Kyaw
@app.route('/hello/<username>')
def hello_user(username):
    return render_template('hello.html', username=username)

if __name__ == "__main__":
    app.run(debug=True)
