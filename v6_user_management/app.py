# app.py
from flask import Flask, redirect, url_for
from auth import auth_bp
from users import users_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)

@app.route('/')
def home():
    return "Welcome to Flask Fundamental 6"

if __name__ == "__main__":
    app.run(debug=True)

