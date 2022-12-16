# Imports
import json
import os
from random import choice
from string import ascii_letters

from flask import request

# Models
from models.assignment import Assignment

# Utilities
from utils.check_file import CheckFile

extensions = {
    "C": "c",
    "C++": "cpp",
    "Java": "java",
    "Python": "py"
}

def CheckAPI():
    output = []
    if request.method == "POST":
        request.form = request.get_json()
        language = request.form.get("assignment_lang")
        program = request.form.get("assignment_program")
        assignment_code = request.form.get("assignment_code")

        assignment = Assignment.query.filter_by(code=assignment_code).first()
        # print(program, assignment)
        if assignment is None:
            return json.dumps("Invalid assignment")


        input_cases = assignment.input_cases
        output_cases = assignment.output_cases
        input_list = []
        for case in input_cases.split("---"):
            case_list = []
            case = case.strip()
            for line in case.split("\n"):
                case_list.append(case.split(" "))
            input_list.append(case_list)

        output_list = []
        for case in output_cases.split("---"):
            case_list = []
            case = case.strip()
            for line in case.split("\n"):
                case_list += case.split(" ")
            output_list.append(case_list)

        # print(input_list, output_list)

        filename = "".join([letter for count in range(10) for letter in choice(ascii_letters)])
        filename = f"{filename}.{extensions[language]}"
        with open(filename, "w+") as run_file:
            for line in program.split("\n"):
                run_file.write(line + "\n")
        if not os.path.exists("compiled"):
            os.mkdir("compiled")

        check_assignment = CheckFile()
        check_assignment.set_file_name(filename)
        check_assignment.set_test_cases( input_list, output_list )
        check_assignment.set_folder("")
        output = check_assignment.run_test()
        # print(output)

        for child in os.listdir("compiled"):
            os.remove(os.path.join("compiled", child))
        os.rmdir("compiled")

        os.remove(filename)

    return json.dumps(output)

def CheckSubmission(assignment_code, language, program):
    assignment = Assignment.query.filter_by(code=assignment_code).first()
    if assignment is None:
        return "ERROR"

    input_cases = assignment.input_cases
    output_cases = assignment.output_cases
    input_list = []
    for case in input_cases.split("---"):
        case_list = []
        case = case.strip()
        for line in case.split("\n"):
            case_list.append(case.split(" "))
        input_list.append(case_list)

    output_list = []
    for case in output_cases.split("---"):
        case_list = []
        case = case.strip()
        for line in case.split("\n"):
            case_list += case.split(" ")
        output_list.append(case_list)

    # print(input_list, output_list)

    filename = "".join([letter for count in range(10) for letter in choice(ascii_letters)])
    filename = f"{filename}.{extensions[language]}"
    with open(filename, "w+") as run_file:
        for line in program.split("\n"):
            run_file.write(line + "\n")
    if not os.path.exists("compiled"):
        os.mkdir("compiled")

    check_assignment = CheckFile()
    check_assignment.set_file_name(filename)
    check_assignment.set_test_cases( input_list, output_list )
    check_assignment.set_folder("")
    output = check_assignment.run_test()
    # print(output)

    for child in os.listdir("compiled"):
        os.remove(os.path.join("compiled", child))
    os.rmdir("compiled")

    os.remove(filename)

    return "".join(["1" if x == "CORRECT" else "0" for x in output[1:]])
