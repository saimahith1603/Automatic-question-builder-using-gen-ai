import hashlib

# Simulate a simple in-memory database for user data (username, password hash, role)
class UserDatabase:
    def __init__(self):
        self.users = {}  # Initialize an empty dictionary to store users

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password, role):
        password_hash = self.hash_password(password)
        self.users[username] = {"password": password_hash, "role": role}  # Store username, password hash, and role

    def verify_user(self, username, password):
        password_hash = self.hash_password(password)
        user = self.users.get(username)
        if user and user["password"] == password_hash:
            return user["role"]  # Return the role if credentials are correct
        return None

user_db = UserDatabase()

def register_user(username, password, role):
    user_db.add_user(username, password, role)

def check_login(username, password):
    return user_db.verify_user(username, password)
