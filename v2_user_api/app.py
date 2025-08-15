# app.py
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

users = {}  # store user data

@app.route('/')
def home():
    return "welcome from flask fundamental"

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
