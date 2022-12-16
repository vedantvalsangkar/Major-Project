# Imports
import os
import zipfile
from datetime import datetime

from flask import render_template, request, flash, redirect, url_for, send_from_directory
from flask import session

# Models
from models.shared import db
from models.student import Student
from models.classroom import Classroom
from models.assignment import Assignment
from models.submission import Submission

# Utilities
from user_management import GetUser
from utils import constants
from check_assigment import CheckSubmission
SUBMISSION_FOLDER = constants.SUBMISSION_FOLDER


def ClassroomCreate():
    if request.method == "GET":
        return render_template("classroom/classroom_create.html")
    elif request.method == "POST":
        class_name = request.form.get("class_name")
        class_desc = request.form.get("class_desc")

        user = GetUser(session["email"])

        classroom = Classroom(class_name, class_desc, teacher=user)
        db.session.add(classroom)
        db.session.commit()

        flash("Classroom created successfully!", "success")
        return redirect(url_for("dashboard"))

def ClassroomMain(class_code):
    classroom = Classroom.query.filter_by(code=class_code).first()
    if classroom is None:
        flash("No class found!", "danger")
        return redirect(url_for("home"))

    user = GetUser(session["email"])
    if not classroom in user.classrooms:
        flash("Access denied to this classroom!", "warning")
        return redirect(url_for("home"))

    return render_template("classroom/classroom_main.html", classroom=classroom, \
            assignments=sorted(classroom.assignments, key=lambda assign: assign.deadline), \
            current_time=datetime.now, strftime=lambda x: x.strftime("%a, %d %b %Y at %I:%M %p"))

def ClassroomAddStudent():
    class_code = request.form.get("class_code")

    classroom = Classroom.query.filter_by(code=class_code).first()
    if classroom is None:
        flash("No class found!", "danger")
        return redirect(url_for("home"))
    user = GetUser(session["email"])
    if classroom in user.classrooms:
        flash(f"Already part of classroom {classroom.name}!", "warning")

    if not user.enroll_in_class(class_code):
        flash(f"Could not add student to classroom {classroom.name}!", "warning")

    db.session.add(user)
    db.session.commit()

    return redirect(url_for("dashboard"))

def ClassroomDelete(class_code):
    classroom = Classroom.query.filter_by(code=class_code).first()
    if classroom is None:
        flash("No class found!", "danger")
        return redirect(url_for("home"))

    user = GetUser(session["email"])

    if not classroom in user.classrooms:
        flash("Access denied to this classroom!", "warning")
        return redirect(url_for("home"))

    for assignment in classroom.assignments:
        AssignmentDelete(assignment.code)

    session.pop("_flashes", None)
    db.session.delete(classroom)
    db.session.commit()

    flash("Classroom deleted successfully!", "success")
    return redirect(url_for("home"))

def ClassroomRemoveStudent(class_code, student_id):
    classroom = Classroom.query.filter_by(code=class_code).first()
    if classroom is None:
        flash("No class found!", "danger")
        return redirect(url_for("home"))

    user = Student.query.filter_by(id=student_id).first()
    if user is None:
        flash("No such student found!", "danger")
    else:
        if classroom.remove_student(user):
            for assignment in classroom.assignments:
                for submission in Submission.query.filter_by(student=user, assignment=assignment).all():
                    if os.path.exists(submission.file_name):
                        os.remove(submission.file_name)

                    if submission in user.submissions:
                        user.submissions.remove(submission)

                    db.session.delete(submission)

            flash(f"Removed {user.name} from classroom!", "success")

            db.session.add(classroom)
            db.session.add(user)
            db.session.commit()
        else:
            flash("Classroom does not contain student", "danger")

def AssignmentCreate(class_code):
    if request.method == "GET":
        session["class_code"] = class_code
        return render_template("assignment/assignment_create.html")
    elif request.method == "POST":
        assignment_name = request.form.get("assignment_name")
        assignment_desc = request.form.get("assignment_desc")
        assignment_input_format = request.form.get("assignment_input_format")
        assignment_output_format = request.form.get("assignment_output_format")

        assignment_input_cases = [request.form.get(k) if request.form.get(k) != "" else None for k in request.form.keys() if k.startswith("assignment_input_case_")]
        assignment_input_cases = "---".join([str(x) for x in assignment_input_cases if x])

        assignment_output_cases = [request.form.get(k) if request.form.get(k) != "" else None for k in request.form.keys() if k.startswith("assignment_output_case_")]
        assignment_output_cases = "---".join([str(x) for x in assignment_output_cases if x])

        # print(assignment_input_cases, assignment_output_cases)

        assignment_constraints = request.form.get("assignment_constraints")
        assignment_deadline = request.form.get('assignment_deadline')
        assignment_deadline = datetime.strptime(assignment_deadline, "%Y-%m-%dT%H:%M")

        user = GetUser(session["email"])

        # return redirect(url_for("classroom_main", class_code=class_code))

        if session.get("class_code") is None:
            flash("Classroom not selected while creating assignment!", "info")
            return redirect(url_for("dashboard"))

        class_code = session["class_code"]
        classroom = Classroom.query.filter_by(code=class_code).first()
        if classroom is None:
            flash("No class found!", "danger")
            return redirect(url_for("dashboard"))

        if not classroom in user.classrooms:
            flash("Access denied to this classroom!", "warning")
            return redirect(url_for("dashboard"))

        assignment = Assignment(assignment_name, assignment_desc, classroom=classroom)
        assignment.update(input_format=assignment_input_format, output_format=assignment_output_format)
        assignment.update(input_cases=assignment_input_cases, output_cases=assignment_output_cases)
        assignment.update(constraints=assignment_constraints, deadline=assignment_deadline)

        db.session.add(assignment)
        db.session.commit()

        # Create assignment upload folder
        if not os.path.exists(os.path.join(SUBMISSION_FOLDER, assignment.code)):
            os.mkdir(os.path.join(SUBMISSION_FOLDER, assignment.code))

        flash("Assignment created successfully!", "success")
        return redirect(url_for("assignment_main", assignment_code=assignment.code))

def AssignmentMain(assignment_code):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        flash("No assignment found!", "danger")
        return redirect(url_for("home"))

    user = GetUser(session["email"])
    if not assignment.classroom in user.classrooms:
        flash("Access denied to this assigment!", "warning")
        return redirect(url_for("home"))

    file_name = os.path.join(SUBMISSION_FOLDER, assignment.code, f"{user.id}_{user.name}.txt")
    submission = Submission.query.filter_by(file_name=file_name).first()

    # print(assignment.classroom.students)
    if request.method == "POST":
        if assignment.deadline < datetime.now():
            flash("Assignment deadline execeeded!", "danger")
        else:
            assignment_program = request.form.get('assignment_program')
            assignment_lang = request.form.get('assignment_lang')

            if not os.path.exists(os.path.join(SUBMISSION_FOLDER, assignment.code)):
                flash("Upload folder not found! Please inform administrator", "danger")
            else:
                result = CheckSubmission(assignment_code, assignment_lang, assignment_program)

                if result is None:
                    flash("Error while submitting assignment!", "warning")
                else:
                    print(file_name)
                    with open(file_name, "w+") as submission_file:
                        for line in assignment_program.split("\n"):
                            submission_file.write(line + "\n")

                    if submission is None:
                        submission = Submission(file_name, assignment, \
                                                    assignment_lang, result, user)
                    else:
                        submission.update(language=assignment_lang, result=result)
                    flash("Assignment submitted successfully!", "success")

                    db.session.add(submission)
                    db.session.commit()


    submission_program = ""
    if submission:
        with open(file_name, "r") as submission_file:
            for line in submission_file.readlines():
                submission_program += line

    return render_template("assignment/assignment_main.html", assignment=assignment, \
                            submission_program=submission_program, submission=submission, \
                            current_time=datetime.now, strftime=lambda x: x.strftime("%a, %d %b %Y at %I:%M %p"), \
                            os_sep=os.path.sep)

def AssignmentEdit(assignment_code):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        flash("No assignment found!", "danger")
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("assignment/assignment_edit.html", assignment=assignment, \
            assignment_deadline=assignment.deadline.strftime("%Y-%m-%dT%H:%M"))
    elif request.method == "POST":
        assignment_name = request.form.get("assignment_name")
        assignment_desc = request.form.get("assignment_desc")
        assignment_input_format = request.form.get("assignment_input_format")
        assignment_output_format = request.form.get("assignment_output_format")

        assignment_input_cases = [k for k in  request.form.keys() if k.startswith("assignment_input_case_")]
        assignment_input_cases = [request.form.get(k) for k in assignment_input_cases]
        assignment_input_cases = [k if k != "" else None for k in assignment_input_cases]
        assignment_input_cases = "---".join([str(x) for x in assignment_input_cases if x])

        assignment_output_cases = [k for k in  request.form.keys() if k.startswith("assignment_output_case_")]
        assignment_output_cases = [request.form.get(k) for k in assignment_output_cases]
        assignment_output_cases = [k if k != "" else None for k in assignment_output_cases]
        assignment_output_cases = "---".join([str(x) for x in assignment_output_cases if x])

        assignment_constraints = request.form.get("assignment_constraints")
        assignment_deadline = request.form.get('assignment_deadline')
        assignment_deadline = datetime.strptime(assignment_deadline, "%Y-%m-%dT%H:%M")

        assignment.update(name=assignment_name, desc=assignment_desc)
        assignment.update(input_format=assignment_input_format, output_format=assignment_output_format)
        assignment.update(input_cases=assignment_input_cases, output_cases=assignment_output_cases)
        assignment.update(constraints=assignment_constraints, deadline=assignment_deadline)

        db.session.add(assignment)
        db.session.commit()

        for submission in assignment.submissions:
            submission_program = ""
            if submission is None:
                continue
            with open(submission.file_name, "r") as submission_file:
                for line in submission_file.readlines():
                    submission_program += line

            result = CheckSubmission(assignment_code, submission.language, submission_program)
            if result is None:
                flash("Error while updating assignment!", "warning")
                break
            else:
                submission.update(result=result)
            db.session.add(submission)
            db.session.commit()

        flash("Assignment updated successfully!", "success")

    return redirect(url_for("assignment_main", assignment_code=assignment.code))

def AssignmentDelete(assignment_code):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        flash("No assignment found!", "danger")
        return redirect(url_for("home"))
    class_code = assignment.classroom.code

    for submission in assignment.submissions:
        submission.delete()
        db.session.delete(submission)

    if os.path.exists(os.path.join(SUBMISSION_FOLDER, assignment.code)):
        file_name = f"{assignment.classroom.name} - {assignment.name} submissions.zip"
        zip_file = os.path.join(SUBMISSION_FOLDER, assignment.code, file_name)
        if os.path.exists(zip_file):
            os.remove(zip_file)
        os.rmdir(os.path.join(SUBMISSION_FOLDER, assignment.code))

    db.session.delete(assignment)
    db.session.commit()

    flash("Assignment deleted successfully!", "success")

    return redirect(url_for("classroom_main", class_code=class_code))

def SubmissionDownload(assignment_code, file_name):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        flash("No assignment found!", "danger")
        return redirect(url_for("dashboard"))

    user = GetUser(session["email"])
    if not assignment.classroom in user.classrooms:
        flash("Access denied to this assigment!", "warning")
        return redirect(url_for("dashboard"))

    folder_name = os.path.join(SUBMISSION_FOLDER, assignment_code)
    submission = Submission.query.filter_by(file_name=os.path.join(folder_name ,file_name)).first()

    if submission is None:
        flash("No such submission!", "warning")
        return redirect(url_for("assignment_main", assignment_code=assignment.code))

    try:
        return send_from_directory(folder_name, file_name, as_attachment=True)
    except Exception:
        flash("Submission file not found!", "warning")
        return redirect(url_for("assignment_main", assignment_code=assignment.code))

def SubmissionDownloadAll(assignment_code):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        flash("No assignment found!", "danger")
        return redirect(url_for("dashboard"))

    user = GetUser(session["email"])
    if not assignment.classroom in user.classrooms:
        flash("Access denied to this assigment!", "warning")
        return redirect(url_for("dashboard"))

    folder_name = os.path.join(SUBMISSION_FOLDER, assignment_code)
    submissions = Submission.query.filter_by(assignment=assignment).all()

    if submissions is None:
        flash("No current submissions!", "warning")
        return redirect(url_for("assignment_main", assignment_code=assignment.code))

    file_name = f"{assignment.classroom.name} - {assignment.name} submissions.zip"
    zip_file = os.path.join(folder_name, file_name)
    if os.path.exists(zip_file):
        os.remove(zip_file)

    arcname = f"{assignment.classroom.name} - {assignment.name} submissions"
    with zipfile.ZipFile(zip_file, "w") as zip_file:
        for submission in submissions:
            if os.path.exists(submission.file_name) and os.path.isfile(submission.file_name):
                zip_file.write(submission.file_name, \
                                os.path.join(arcname, submission.file_name.split(os.path.sep)[-1]))

    try:
        return send_from_directory(folder_name, arcname + ".zip", as_attachment=True)
    except Exception:
        flash("Submission file not found!", "warning")
        return redirect(url_for("assignment_main", assignment_code=assignment.code))

def SubmissionDownloadResults(assignment_code, host_url):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        flash("No assignment found!", "danger")
        return redirect(url_for("dashboard"))

    user = GetUser(session["email"])
    if not assignment.classroom in user.classrooms:
        flash("Access denied to this assigment!", "warning")
        return redirect(url_for("dashboard"))

    folder_name = os.path.join(SUBMISSION_FOLDER, assignment_code)
    submissions = Submission.query.filter_by(assignment=assignment).all()

    if submissions is None:
        flash("No current submissions!", "warning")
        return redirect(url_for("assignment_main", assignment_code=assignment.code))

    file_name = f"{assignment.classroom.name} - {assignment.name} results.csv"
    csv_file = os.path.join(folder_name, file_name)
    if os.path.exists(csv_file):
        os.remove(csv_file)

    base_url = ":".join(host_url.split(":")[:2])

    with open(csv_file, "w+") as open_csv:
        open_csv.write("Sr No., Classroom, Name, Email, Language, Results, Download Link\n")
        for idx, student in enumerate(assignment.classroom.students):
            for submission in assignment.submissions:
                if submission.student.id == student.id:
                    file_name = submission.file_name.split(os.path.sep)[-1]
                    open_csv.write(f"{idx}, {submission.assignment.classroom.name}, {student.name}, ")
                    open_csv.write(f"{student.email}, {submission.language}, {submission.result}, ")
                    open_csv.write(f"'{base_url}/submission/download/{assignment_code}/{file_name}'\n")
                    break
            else:
                open_csv.write(f"{idx}, {submission.assignment.classroom.name}, {student.name}, ")
                open_csv.write(f"{student.email}, Not submitted, Not submitted, Not submitted\n")


    try:
        file_name =  f"{assignment.classroom.name} - {assignment.name} results.csv"
        return send_from_directory(folder_name, file_name, as_attachment=True)
    except Exception:
        flash("Submission file not found!", "warning")
    return redirect(url_for("assignment_main", assignment_code=assignment.code))
