from flask import Flask, jsonify, request , session
# from flask_sqlalchemy import SQLAlchemy
import psycopg2
import bcrypt
# from flask_bcrypt import Bcrypt, check_password_hash
# import os
from psycopg2 import sql

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


app = Flask(__name__)
app.config['SECRET_KEY'] = 'task'


#___________________________________________Admin_______________________________________________________________


from admin.model import *
@app.route('/api/admin/teachers', methods=['POST', 'GET'])
def teachers():
    return manage_teachers()

#___________________________________________Teacher______________________________________________________________

from mentor.model import *
@app.route('/api/teacher/students/<string:teacherid>', methods=['POST', 'GET'])
def students(teacherid):
    return manage_students(teacherid)

@app.route('/api/teacher/announcements/<string:teacherid>', methods=['POST', 'GET'])
def announcements(teacherid):
    return manage_announcements(teacherid)

@app.route('/api/teacher/task/<string:teacherid>', methods=['POST', 'GET'])
def task(teacherid):
    return add_task(teacherid)

@app.route('/api/teacher/taskSubmitted/<string:teacherid>', methods=['GET'])
def taskSubmitted(teacherid):
    return view_submitted_task(teacherid)

@app.route('/api/teacher/taskSubmitted/marks/<string:submissionid>', methods=['PUT'])
def marks(submissionid):
    return add_marks(submissionid)

@app.route('/api/teacher/students/deleteStudent/<string:studentid>', methods=['DELETE'])
def deleteStudent(studentid):
    return delete_student(studentid)

from login import *
@app.route('/api/login', methods=['POST'])
def userlogin():
    return login()

@app.route('/api/teacher/task/updatingTask/<string:taskid>', methods=['DELETE'])
def Taskdelete(taskid):
    return deleteTask(taskid)

if __name__ == '__main__':
    app.run(debug=True)
