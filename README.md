# Coding Classroom 💻📚

> Platform for both teachers and students where they can share and submit programming (coding) assignments.

### Features:
For teachers
1. Create classrooms.
2. Allow the students to join the classroom (using a class code).
3. Remove students from classrooms (if required).
4. Create programming assignments with any number of test cases
5. Automatic grading of assignments (based on given test cases).
6. Add/remove test cases even after assignment submission.
7. Download the grades (as CSV).
8. Download individual or the all the submission files.

For students
1. Join a classroom (using a given class code).
2. View all the assignments in a grid layout.
3. Submit the assignment in any language of choice
   _(currently C, C++, Java and Python but can be extended)_
4. Write your code in a user-friendly code editor which supports syntax highlighting, bracket completion and many visual themes.

### Tools Used
Backend
- [Flask]
- [Flask-SQLAlchemy]
- [Subprocess] module (Python) (for executing the code.)
- [Bcrypt] (for password hashing.)

Frontend
- [Bootstrap 4]
- [Jinja] templating
- [CodeMirror] API (for the awesome code editor.)


## Note
> This project is just a simple attempt at creating a code executing API.
> **Executing code given from strangers on your computer (or server) can be dangerous.** Security vulnerabilities have not been throughly checked, so be cautious.

### Installation
> Make sure you have Python 3.x installed.
```
$ cd Coding-Classroom
$ pip install -r requirements.txt
$ python server.py
```
_(If you get any python or pip not found errors, try using python3 or pip3 instead)_

Using a Python virtual environment is recommended

```
$ python -m venv env
$ .\env\Scripts\activate
$ pip install -r requirements.txt
```

### Todo
- Optimize the assignment execution time.
- Find any security related issues in the solve them.
- Add more languages.

[//]:
Links
[Flask]: <https://flask.palletsprojects.com/en/1.1.x/>
[Flask-SQLAlchemy]: <https://flask-sqlalchemy.palletsprojects.com/en/2.x/>
[Subprocess]: <https://docs.python.org/3/library/subprocess.html>
[Bcrypt]: <https://github.com/pyca/bcrypt/>

[Bootstrap 4]: <https://getbootstrap.com/>
[Jinja]: <https://jinja.palletsprojects.com/en/2.11.x/>
[CodeMirror]: <https://codemirror.net/>
