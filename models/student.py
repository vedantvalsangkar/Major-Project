from models.shared import db
from models.shared import User
from models.classroom import Classroom

# Utilities
from utils.hashing import generate_hash

students = db.Table("students",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
    db.Column("classroom_id", db.Integer, db.ForeignKey("classroom.id"))
)

class Student(db.Model, User):

    classrooms = db.relationship("Classroom",   secondary=students, \
                                                backref=db.backref("students", lazy=True) )
    submissions = db.relationship("Submission", backref="student", lazy=True)

    def __init__(self, name, email, password):
        self.user_type = "student"
        self.name = name
        self.email = email
        self.password = generate_hash(password)
        self.verified = False

    def get_classes(self):
        return self.classrooms

    def get_submissions(self):
        return self.submissions

    def enroll_in_class(self, code):
        classroom = Classroom.query.filter_by(code=code).first()
        if classroom is None:
            return False
        self.classrooms.append(classroom)

        return True
