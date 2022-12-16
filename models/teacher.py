from models.shared import db
from models.shared import User
from models.classroom import Classroom

# Utilities
from utils.hashing import generate_hash

class Teacher(db.Model, User):

    classrooms = db.relationship("Classroom", backref="teacher", lazy=True)

    def __init__(self, name, email, password):
        self.user_type = "teacher"
        self.name = name
        self.email = email
        self.password = generate_hash(password)
        self.verified = False

    def get_classes(self):
        return Classroom.query.filter_by(teacher_id=self.id).all()
