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

#____________________________________View Task by Student_______________________________________________
   
@app.route('/api/student/task/<string:classno>', methods=['GET'])
def task(classno):
    return view_task(classno)
    
#_____________________________view Announcement by students______________________________________________
@app.route('/api/student/announcement/<string:classno>', methods=['GET'])
def announcement(classno):
    return view_announcement(classno)

#________________________________Task submission by students_________________________________________________
 
@app.route('/api/student/task/submit/<string:taskid>', methods=['POST'])
def submit_task(taskid):
    return task_submission(taskid)

#________________________________update submitted task by students_____________________________________________

@app.route('/api/student/task/update/<string:submissionid>', methods=['PUT'])
def update_task(submissionid):
    return task_updation(submissionid)

#________________________________delete submitted task by students_____________________________________________

@app.route('/api/student/task/delete/<string:submissionid>', methods=['DELETE'])
def delete_task(submissionid):
    return task_deletion(submissionid)

#_______________________________task priority list____________________________________________________________

@app.route('/api/student/tasklist/<string:studentid>', methods=['GET'])
def task_list(studentid):
    return tasklist_view(studentid)

#__________________________________________student chat section_______________________________________________

@app.route('/api/student/task/chat/<string:senderid>', methods=['GET', 'POST'])
def studentchat(senderid):
  return chat(senderid)

#__________________________________________teacher chat section_______________________________________________
@app.route('/api/teacher/task/chat/<string:senderid>', methods=['GET', 'POST'])
def teacherchat(senderid):
    return chatteacher(senderid)

#_______________________________send mail by type____________________________________________________________
@app.route('/api/email/<string:type>', methods=['POST'])
def email_type(type):
    return send_email(type)    
#_____________________________mail forgot password_____________________________________________ 
@app.route('/api/email/forgotpwd', methods=['POST'])
def password_forgot():
    return forgot_password()
    
#_________________________link for change password____________________________
@app.route('/api/email/forgotpwd/newpassword/<string:email>', methods=['POST']) 
def password_new(email):
    return new_password(email)   
       
  
if __name__ == '__main__':
    app.run(debug=True, port=5001)
