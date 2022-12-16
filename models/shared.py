from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User():
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    user_type = db.Column(db.String(20), nullable=False)
    verified = db.Column(db.Boolean, default=False)
