from werkzeug.security import generate_password_hash

users = {
    "admin": {
        "username": "admin",
        "age": 30,
        "password_hash": generate_password_hash("adminpass"),
        "role": "admin"
    }
}
