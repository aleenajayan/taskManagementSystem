from connection import *
from flask import Flask
import psycopg2 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from model import *
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from email.mime.text import MIMEText

app = Flask(__name__)

connection = psycopg2.connect(**db_params)
cursor = connection.cursor()

#View Task by Student  
@app.route('/api/student/task/<string:classno>', methods=['GET'])
def task_view(classno):
    return view_task(classno)
    
#view Announcement by students
@app.route('/api/student/announcement/<string:classno>', methods=['GET'])
def announcement(classno):
    return view_announcement(classno)

#Task submission by students
 
@app.route('/api/student/task/submit/<string:taskid>', methods=['POST'])
def submit_task(taskid):
    return task_submission(taskid)

#update submitted task by students

@app.route('/api/student/task/update/<string:submissionid>', methods=['PUT'])
def update_task(submissionid):
    return task_updation(submissionid)

#delete submitted task by students

@app.route('/api/student/task/delete/<string:submissionid>', methods=['DELETE'])
def delete_task(submissionid):
    return task_deletion(submissionid)

#view score by students
@app.route('/api/student/score/<string:submissionid>', methods=['GET'])
def score(submissionid):
    return score_view(submissionid)

#task priority list

@app.route('/api/student/tasklist/<string:studentid>', methods=['GET'])
def task_list(studentid):
    return tasklist_view(studentid)

#student chat section

@app.route('/api/student/task/chat/<string:senderid>', methods=['GET', 'POST'])
def studentchat(senderid):
  return chat(senderid)

#teacher chat section
@app.route('/api/teacher/task/chat/<string:senderid>', methods=['GET', 'POST'])
def teacherchat(senderid):
    return chatteacher(senderid)
#status update
@app.route('/api/student/task/updateStatus/<string:taskid>', methods=['POST'])
def updateStatus(taskid):
    return statusUpdate(taskid)
       
#send mail by type
@app.route('/api/email/<string:type>', methods=['POST'])
def email_type(type):
    return send_email(type)    
#mail forgot password
@app.route('/api/email/forgotpwd', methods=['POST'])
def password_forgot():
    return forgot_password()
    
#link for change password
@app.route('/api/email/forgotpwd/newpassword/<string:email>', methods=['POST']) 
def password_new(email):
    return new_password(email)   
      
  
if __name__ == '__main__':
    app.run(debug=True, port=5000)
