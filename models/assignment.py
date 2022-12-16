from random import choices
from string import ascii_letters

from models.shared import db

ASSIGNMENT_CODE_LENGTH = 6

class Assignment(db.Model):
    # assignments = db.relationship("Assignment", backref="classroom", lazy=True)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.String(80), nullable=True)
    code = db.Column(db.String(ASSIGNMENT_CODE_LENGTH), nullable=False, unique=True)
    input_format = db.Column(db.String(80), nullable=False)
    output_format = db.Column(db.String(80), nullable=False)
    input_cases = db.Column(db.String(80), nullable=False)
    output_cases = db.Column(db.String(80), nullable=False)
    constraints = db.Column(db.String(80), nullable=True)

    deadline = db.Column(db.DateTime, nullable=True)

    classroom_id = db.Column(db.Integer, db.ForeignKey("classroom.id"))
    submissions = db.relationship("Submission", backref="assignment", lazy=True)

    def __init__(self, name, desc, classroom, deadline=None):
        self.name = name
        self.desc = desc
        self.code = self.generate_assignment_code()
        self.classroom = classroom
        self.deadline = deadline

    def generate_assignment_code(self):
        code = "".join(choices(ascii_letters, k=ASSIGNMENT_CODE_LENGTH))
        while True:
            if Assignment.query.filter_by(code=code).first() is None:
                break
            code = "".join(choices(ascii_letters, k=ASSIGNMENT_CODE_LENGTH))
        return code

    def update(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
