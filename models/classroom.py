from random import choices
from string import ascii_letters

from models.shared import db

CLASS_CODE_LENGTH = 6

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.String(80), nullable=True)
    code = db.Column(db.String(CLASS_CODE_LENGTH), nullable=False, unique=True)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))
    student_ids = db.Column(db.Integer, db.ForeignKey("student.id"))

    assignments = db.relationship("Assignment", backref="classroom", lazy=True)

    def __init__(self, name, desc, teacher):
        self.name = name
        self.desc = desc
        self.code = self.generate_class_code()
        self.teacher = teacher

    def generate_class_code(self):
        code = "".join(choices(ascii_letters, k=CLASS_CODE_LENGTH))
        while True:
            if Classroom.query.filter_by(code=code).first() is None:
                break
            code = "".join(choices(ascii_letters, k=CLASS_CODE_LENGTH))
        return code

    def enroll_student(self, student):
        self.students.append(student)

    def remove_student(self, student):
        if student in self.students:
            self.students.remove(student)
            return True
        return False
