import bcrypt

FORMAT = "utf-8"

def generate_hash(password):
    return bcrypt.hashpw(password.encode(FORMAT), bcrypt.gensalt())

def check_password(original, password):
    return bcrypt.checkpw(password.encode(FORMAT), original)
