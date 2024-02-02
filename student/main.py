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

#_______________________________send mail by type____________________________________________________________

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tarentotask@gmail.com'
app.config['MAIL_PASSWORD'] = 'upok lnov qiri nbjs'
app.config['MAIL_DEFAULT_SENDER'] = 'tarentotask@gmail.com'

mail = Mail(app)

@app.route('/api/email/<string:type>', methods=['POST'])
def send_email(type):
    try:         
       data = request.get_json()
       subject = data['subject']
       body = data['message_body']
   
       fetch_emails_query = "SELECT email FROM login WHERE type = %s"
       cursor.execute(fetch_emails_query, (type,))
       emails = cursor.fetchall()
       
       if not emails:
               return jsonify({'error': 'No emails found for the specified user type'})
   
        
       for email in emails:
          recipient_email = email[0]
          message = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
          message.body = body
          mail.send(message)
          return jsonify({'message': 'Email sent successfully!'})
          
    except Exception as e:
        return jsonify(f'Error sending email: {str(e)}', 'error')  
    

#_____________________________mail forgot password____________________________  

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)
    
      
#      Collect data from the request JSON
#         data = request.get_json()
#         subject = data['subject']
#         body = data['message_body']

#         # Fetch all emails based on the user type from the login table
#         fetch_emails_query = "SELECT email FROM login WHERE type = %s"
#         cursor.execute(fetch_emails_query, (type,))
#         emails = cursor.fetchall()

#         if not emails:
#             return jsonify({'error': 'No emails found for the specified user type'})

#         # Send emails to each email address
#         for email in emails:
#             recipient_email = email[0]

#             # Create a Flask-Mail Message object
#             message = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
#             message.body = body

#             # Send the email
#             mail.send(message)
#         connection.commit()
