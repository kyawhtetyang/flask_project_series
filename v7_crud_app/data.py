# data.py
from werkzeug.security import generate_password_hash

users = {
    "admin": {
        "username": "admin",
        "age": 30,
        "password_hash": generate_password_hash("adminpass"),
        "role": "admin",
        "email": "admin@example.com",
        "bio": "I manage this app",
        "profile_pic": None
    },
    "editor1": {
        "username": "editor1",
        "age": 28,
        "password_hash": generate_password_hash("editorpass"),
        "role": "editor",
        "email": "editor1@example.com",
        "bio": "I can edit users",
        "profile_pic": None
    },
    "viewer1": {
        "username": "viewer1",
        "age": 25,
        "password_hash": generate_password_hash("viewerpass"),
        "role": "viewer",
        "email": "viewer1@example.com",
        "bio": "I can only view",
        "profile_pic": None
    }
}
