# app.py
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome home"

@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')  # fixed .args and default value
    return f"Hello, {name}!"

@app.route('/postdata', methods=['POST'])
def postdata():
    data = request.get_json()
    return jsonify({"you said": data})

@app.route('/hello/<username>')
def hello_user(username):
    return render_template('hello.html', username=username)  # fixed filename

if __name__ == '__main__':
    app.run(debug=True)
