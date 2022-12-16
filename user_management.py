from flask import render_template, request, flash, redirect, url_for
from flask import session

# Models
from models.shared import db, User
from models.student import Student
from models.teacher import Teacher

# Utilities
from utils.hashing import check_password

def LoginUser():
    if request.method == "GET":
        flash("Please login first!! (GET method used for login)", "info")
        return redirect(url_for("home"))

    email = request.form.get("email")                   # Email
    password = request.form.get("password")             # Password

    resp = GetUser(email)
    if not isinstance(resp, User):
        return resp

    user = resp

    if check_password(user.password, password):
        session["name"] = user.name
        session["email"] = user.email
        session["verified"] = user.verified
        session["user_type"] = user.user_type
    else:
        flash("Incorrect email or password!", "danger")
        return redirect(url_for("home"))

    flash("Logged in successfully!", "success")
    return redirect(url_for("dashboard"))

def RegisterUser():
    if request.method == "GET":
        flash("Please login first!! (GET method used for registration)", "info")
        return redirect(url_for("home"))

    user_type = request.form.get("user_type")           # Student or Teacher
    name = request.form.get("name")                     # Name
    email = request.form.get("email")                   # Email
    password = request.form.get("password")             # Password
    verify_password = request.form.get("verify_password")


    if password != verify_password:
        flash("Password and verified password do not match!", "warning")
        return redirect(url_for("home"))

    if Teacher.query.filter_by(email=email).first() or Student.query.filter_by(email=email).first():
        flash(f"User with email {email} already exists!", "danger")
        return redirect(url_for("home"))

    newUser = None
    if user_type == "student":
        newUser = Student(name, email, password)
    elif user_type == "teacher":
        newUser = Teacher(name, email, password)
    else:
        flash(f"Invalid user type {user_type}!", "danger")
        return redirect(url_for("home"))
    db.session.add(newUser)
    db.session.commit()

    session["name"] = newUser.name
    session["email"] = newUser.email
    session["verified"] = newUser.verified
    session["user_type"] = newUser.user_type

    flash("Registered successfully!", "success")
    return redirect(url_for("dashboard"))

def LogoutUser():
    if request.method == "GET":
        flash("Please login first! (GET method used for logout)", "info")
        return redirect(url_for("home"))

    del session["name"]
    del session["email"]
    del session["user_type"]
    del session["verified"]

    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))

def AuthorizeUser(user_type=None):
    is_authorized = True
    if session.get("name") is not None and session.get("email") is not None:
        if user_type is not None and session.get("user_type") != user_type:
            is_authorized = False
    else:
        is_authorized = False

    return is_authorized

def GetUser(email):

    user = None
    user = Student.query.filter_by(email=email).first()

    if user:
        return user

    user = Teacher.query.filter_by(email=email).first()
    if user:
        return user

    flash(f"No such user with email {email}!", "danger")
    return redirect(url_for("home"))

### Dashboards

def TeacherDashboard():
    user = GetUser(session["email"])
    user_type = session["user_type"]

    classes = []
    if user_type == "teacher":

        for _class in user.get_classes():
            classes.append({
                "name": _class.name,
                "desc": _class.desc,
                "code": _class.code,
            })
            if len(_class.assignments) > 0:
                classes[-1]["assignment"] = _class.assignments[-1]
            else:
                classes[-1]["assignment"] = None
    return render_template("dashboard/teacher_dashboard.html", classes=classes)

def StudentDashboard():
    user = GetUser(session["email"])
    user_type = session["user_type"]

    classes = []
    if user_type == "student":
        for _class in user.get_classes():
            classes.append({
                "name": _class.name,
                "desc": _class.desc,
                "code": _class.code,
            })
            if len(_class.assignments) > 0:
                classes[-1]["assignment"] = _class.assignments[-1]
            else:
                classes[-1]["assignment"] = None

    return render_template("dashboard/student_dashboard.html", classes=classes)
