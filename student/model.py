from connection import *
from flask import Flask, jsonify, request , session
import psycopg2 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from urllib.parse import urlparse, parse_qs
from datetime import datetime

connection = psycopg2.connect(**db_params)
cursor = connection.cursor()



#____________________________________View Task by Student_______________________________________________
def view_task(classno):
    try:
        select_query = """
        SELECT t.duedate, t.question, te.name
        FROM task t
        JOIN teacher te ON t.teacherid = te.teacherid
        WHERE t.classno = %s;
        """
        cursor.execute(select_query, (classno,))
        tasks = cursor.fetchall()

        tasks_data = [
            {
                'duedate': task[0],
                'question': task[1],
                'teachername': task[2]
            }
            for task in tasks
        ]

        return jsonify({'tasks': tasks_data})
    except Exception as e:
        return jsonify({'error': str(e)})

#_____________________________view Announcement by students______________________________________________

def view_announcement(classno):
    try:
        select_query = """
        SELECT announcement.announcement, teacher.name
        FROM announcement
        JOIN teacher ON announcement.teacherid = teacher.teacherid
        WHERE announcement.classno = %s OR announcement.classno = 'all'
        """
        cursor.execute(select_query, (classno,))
        announcements = cursor.fetchall()

        # Check if there are no announcements
        if not announcements:
            return jsonify({'error': 'There are no announcements for this class.'})

        announcements_data = [
            {
                'announcement': announcement[0],
                'Teacher Name': announcement[1]
            }
            for announcement in announcements
        ]

        return jsonify({'announcements': announcements_data})
    except Exception as e:
        return jsonify({'error': str(e)})

#________________________________Task submission by students_____________________________________________

drive_credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive.file'])
def upload_to_google_drive(file_path, file_name, folder_id):
    try:
        drive_service = build('drive', 'v3', credentials=drive_credentials)

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]  
        }
        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webContentLink'
        ).execute()

        return file.get('webContentLink')
    except Exception as e:
        return str(e)
  
def task_submission(taskid):
    try:
        file = request.files['file']
        file.save('temp_file')
        classno = request.form['classno']
        studentid = request.form['studentid']
        if not classno:
            return jsonify({'error': 'Class number (classno) is required for task submission.'})

        check_existing_query = """
            SELECT COUNT(*)
            FROM tasksubmission
            WHERE studentid = %s AND teacherid = (
                SELECT teacherid FROM task WHERE taskid = %s
            ) AND taskid = %s;
        """
        cursor.execute(check_existing_query, (studentid, taskid, taskid))
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            return jsonify({'error': 'Task submission already exists for this task.'})

        select_due_date_query = "SELECT duedate FROM task WHERE taskid = %s"
        cursor.execute(select_due_date_query, (taskid,))
        due_date = cursor.fetchone()[0]
        due_date = datetime.strptime(str(due_date), "%Y-%m-%d")

        current_date = datetime.now()
        if current_date > due_date:
            return jsonify({'error': 'Task submission is past the due date.'})

        select_teacher_query = "SELECT teacherid FROM task WHERE taskid = %s"
        cursor.execute(select_teacher_query, (taskid,))
        teacherid = cursor.fetchone()[0]

        folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'

        file_url = upload_to_google_drive('temp_file', file.filename, folder_id)

        insert_query = """
            INSERT INTO tasksubmission (file, classno, teacherid, studentid, taskid)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (  
            file_url,
            classno,
            teacherid,
            studentid,
            taskid,))
        connection.commit()
                
        check_entry_query = """
            SELECT * FROM tracking
            WHERE taskid = %s AND studentid = %s AND teacherid = %s
        """
        cursor.execute(check_entry_query, (taskid, studentid, teacherid))
        existing_entry = cursor.fetchone()
 
        if existing_entry:
            status="completed"
            update_query = """
                UPDATE tracking
                SET status = %s
                WHERE taskid = %s AND studentid = %s AND teacherid = %s
                """
            cursor.execute(update_query, (status, taskid, studentid, teacherid))
 
            connection.commit()
        else:
            insert_query = """
                INSERT INTO tracking (status, teacherid, studentid, taskid)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                status,
                teacherid,
                studentid,
                taskid,
            ))
            connection.commit()

        return jsonify({'message': 'Task submitted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

    
#________________________________update submitted task by students_____________________________________________
def extract_file_id(file_url):
    parsed_url = urlparse(file_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('id', [None])[0]

def delete_file(file_id):
    try:
      
        drive_service = build('drive', 'v3', credentials=drive_credentials)
    
        drive_service.files().delete(fileId=file_id).execute()

        return {'message': 'File deleted successfully'}

    except Exception as e:
        return {'error': str(e)} 
  

def task_updation(submissionid):
    try:
    
        fetch_url_query = """
        SELECT file FROM tasksubmission WHERE submissionid = %s;
        """
        cursor.execute(fetch_url_query, (submissionid,))
        existing_file_url = cursor.fetchone()

        if not existing_file_url:
            return jsonify({'error': 'No file found for the given submissionid'})

        existing_file_id = extract_file_id(existing_file_url[0])

        if existing_file_id:
            result = delete_file(existing_file_id)
            print(result)
        else:
            print("Unable to extract file ID from the existing URL.")

        file = request.files['file']
        file.save('temp_file')
        folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'
        file_url = upload_to_google_drive('temp_file', file.filename, folder_id)

        update_query = """
        UPDATE tasksubmission
        SET file=%s
        WHERE submissionid = %s;
        """
        print("Executing query:", update_query)
        print("Values:", (file_url, submissionid))

        cursor.execute(update_query, (file_url, submissionid))
        connection.commit()

        return jsonify({'message': 'File .updated ', 'file_url': file_url})

    except Exception as e:
        return jsonify({'error': str(e)})


#________________________________delete submitted task by students_____________________________________________

def task_deletion(submissionid):
    try:
        fetch_url_query = """
        SELECT file FROM tasksubmission WHERE submissionid = %s;
        """
        cursor.execute(fetch_url_query, (submissionid,))
        existing_file_url = cursor.fetchone()

        if not existing_file_url:
            return jsonify({'error': 'No file found for the given submissionid'})

        existing_file_id = extract_file_id(existing_file_url[0])

        if existing_file_id:
            result = delete_file(existing_file_id)
            print(result)
        else:
            print("Unable to extract file ID from the existing URL.")
    
        delete_query = """
            DELETE FROM tasksubmission
            WHERE submissionid = %s;
        """
        
        cursor.execute(delete_query, (submissionid,))
        connection.commit()
        


        return jsonify({'message': 'File deleted '})

    except Exception as e:
        return jsonify({'error': str(e)})

#_______________________________task priority list____________________________________________________________

    
from datetime import datetime

def tasklist_view(student_id):
    try:
    
        select_classno_query = "SELECT classno FROM student WHERE studentid = %s"
        cursor.execute(select_classno_query, (student_id,))
        classno = cursor.fetchone()

        if not classno:
            return jsonify({'error': 'Student not found'})

        classno = classno[0]

        current_date = datetime.now()
        # current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

        select_query = """
        SELECT t.duedate, t.question, te.name
        FROM task t
        JOIN teacher te ON t.teacherid = te.teacherid
        WHERE t.classno = %s
        AND t.duedate >= %s
        AND NOT EXISTS (
            SELECT 1
            FROM tasksubmission ts
            WHERE ts.taskid = t.taskid
            AND ts.studentid = %s
        );
        """
        cursor.execute(select_query, (classno, current_date, student_id))
        tasks = cursor.fetchall()
        connection.commit()
        
        tasks_data = [
            {
                'duedate': task[0],
                'question': task[1],
                'teachername': task[2]
            }
            for task in tasks
        ]

        return jsonify({'tasks': tasks_data})
    except Exception as e:
        return jsonify({'error': str(e)}) 
#________________________________view score_____________________________________
def score_view(submissionid):
    try:
        score_query = "SELECT score , file  FROM tasksubmission WHERE submissionid = %s"
        cursor.execute(score_query, (submissionid,))
        score = cursor.fetchall()
        return jsonify({'score': score})
    except Exception as e:
        return jsonify({'error': str(e)})
#__________________________________________student chat section_______________________________________________


def chat(senderid):
    if request.method == 'POST':
        try:
            data = request.get_json()
            print("_________",data)

            if 'taskid' not in data:
                return jsonify({'error': 'Please provide taskid in the request data.'}), 400

            fetch_teacher_query = "SELECT teacherid FROM task WHERE taskid = %s;"
            cursor.execute(fetch_teacher_query, (data['taskid'],))
            teacherid = cursor.fetchone()

            if not teacherid:
                return jsonify({'error': 'Invalid taskid'}), 400
            if 'message' not in data or not data['message'].strip():  
                return jsonify({'error': 'Please provide non-empty content in the request data.'}), 400
            
            sendertype= 'student'

            query = "INSERT INTO chat (senderid, receiverid, taskid, content, sendertype) VALUES (%s, %s, %s, %s, %s);"
            cursor.execute(query, (senderid, teacherid[0], data['taskid'] ,data['message'],sendertype))
            connection.commit()
            print("_____________________",query)

            return jsonify({'message': 'Chat added successfully!'})

        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500
    else:
        data = request.get_json()
        if 'taskid' not in data:
            return jsonify({'error': 'Please provide taskid in the request data.'}), 400

        fetch_teacher_query = "SELECT teacherid FROM task WHERE taskid = %s;"
        cursor.execute(fetch_teacher_query, (data['taskid'],))
        teacherid = cursor.fetchone()

        if not teacherid:
            return jsonify({'error': 'Invalid taskid'}), 400

        query = """
            SELECT 
                c.content, 
                c.timestamp, 
                CASE 
                    WHEN c.sendertype = 'student' THEN s.name 
                    WHEN c.sendertype = 'teacher' THEN t.name 
                END AS sender_name
            FROM chat c
            LEFT JOIN student s ON c.senderid = s.studentid AND c.sendertype = 'student'
            LEFT JOIN teacher t ON c.senderid = t.teacherid AND c.sendertype = 'teacher'
            WHERE (c.senderid = %s AND c.receiverid = %s)
            OR (c.senderid = %s AND c.receiverid = %s)
            ORDER BY c.timestamp;
        """

        print("____query_____", query)

        cursor.execute(
            query,
            (senderid, teacherid[0], senderid, teacherid[0])
        )

        chat_history = cursor.fetchall()
        return jsonify({'chat_history': chat_history})

#__________________________________________teacher chat section_______________________________________________


def chatteacher(senderid):
    if request.method == 'POST':
        try:
            data = request.get_json()
            print("_________",data)

            if 'taskid' not in data:
                return jsonify({'error': 'Please provide taskid in the request data.'}), 400
            # fetch_teacher_query = "SELECT classno FROM task WHERE taskid = %s;"
            # cursor.execute(fetch_teacher_query, (data['taskid'],))
            # classno = cursor.fetchone()
            
            if 'studentid' not in data:
                return jsonify({'error': 'Please provide taskid in the request data.'}), 400
            
            if 'message' not in data or not data['message'].strip(): 
                return jsonify({'error': 'Please provide non-empty content in the request data.'}), 400
            
            sendertype= 'teacher'

            query = "INSERT INTO chat (senderid, receiverid, taskid, content, sendertype) VALUES (%s, %s, %s, %s,%s);"
            cursor.execute(query, (senderid, data['studentid'], data['taskid'] ,data['message'],sendertype))
            connection.commit()
            print("_____________________",query)

            return jsonify({'message': 'Chat added successfully!'})

        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500
    else:
        try:
            data = request.get_json()
            # if 'receiverid' not in data:
            #     return jsonify({'error': 'Please provide receiver_id in the request data.'}), 400
            if 'taskid' not in data:
                return jsonify({'error': 'Please provide taskid in the request data.'}), 400

            teacherid = senderid

            query = """
               SELECT 
                c.content, 
                c.timestamp, 
                CASE 
                    WHEN c.sendertype = 'student' THEN s.name 
                    WHEN c.sendertype = 'teacher' THEN t.name 
                END AS sender_name
            FROM chat c
            LEFT JOIN student s ON c.senderid = s.studentid AND c.sendertype = 'student'
            LEFT JOIN teacher t ON c.senderid = t.teacherid AND c.sendertype = 'teacher'
            WHERE (c.senderid = %s AND c.receiverid = %s)
            OR (c.senderid = %s AND c.receiverid = %s)
            ORDER BY c.timestamp;
            """
            cursor.execute(query, (senderid, teacherid, teacherid, senderid))
            chat_history = cursor.fetchall()

            return jsonify({'chat_history': chat_history})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        
#_______________________________send mail by type____________________________________________________________
from flask import Flask, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tarentotask@gmail.com'
app.config['MAIL_PASSWORD'] = 'upok lnov qiri nbjs'
app.config['MAIL_DEFAULT_SENDER'] = 'tarentotask@gmail.com'

mail = Mail(app)

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
         print(f'Error sending email: {str(e)}')
         return jsonify({'error': 'Failed to send email'}), 500
#_____________________________mail forgot password____________________________  
 
def forgot_password():
    try:
       data = request.get_json()
       email = data['email']
       subject = 'Forget Password' 
       body = 'Click is this link to change your password '
       
       if 'email' not in data or not data['email'].strip():
        return jsonify({'error': 'Email is required and cannot be empty or contain only spaces'})
 
    
       if '@' not in data['email'] or '.' not in data['email']:
         return jsonify({'error': 'Invalid email format'})
     
       query ="SELECT username, password FROM login WHERE email=%s"
       cursor.execute(query, (email,))
       data = cursor.fetchall()
       
       if not data :
           return jsonify({'error': 'Give the registered email id'})
       else:
          recipient_email = email
          message = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
          message.body = body
          mail.send(message)
          return jsonify({'message': 'Email sent successfully!'})
               
    except Exception as e:
        return jsonify(f'Error sending email: {str(e)}', 'error') 
#_________________________link for change password____________________________
def new_password(email):
    try:
        data = request.get_json()
        new_password = data['new_password']
        
        update_query = "UPDATE login SET password = %s WHERE email = %s"
        cursor.execute(update_query, (new_password, email))
        connection.commit()

        return jsonify({'message': 'Password updated successfully'})
    except Exception as e:
        return jsonify({'error': f'Error updating password: {str(e)}'})

#________________________________status update______________________________
def statusUpdate(taskid):
    try:
        data = request.get_json()
        status = data['status']
        studentid = data['studentid']
        if not data['status'].strip() or not data['studentid'].strip():
                return jsonify({'error': 'status and studentid must have non-empty values'}), 400
        
        if data['status']== 'completed' or data['status']== 'Completed'or data['status']== 'COMPLETED':
            return jsonify({'error': 'Submit the task file'}), 400
 
 
        # status = request.form['classno']
        # studentid = request.form['studentid']
        select_teacher_query = "SELECT teacherid FROM task WHERE taskid = %s"
        cursor.execute(select_teacher_query, (taskid,))
        teacherid = cursor.fetchone()[0]
 
        check_entry_query = """
            SELECT * FROM tracking
            WHERE taskid = %s AND studentid = %s AND teacherid = %s
        """
        cursor.execute(check_entry_query, (taskid, studentid, teacherid))
        existing_entry = cursor.fetchone()
 
        if existing_entry:
            check_entry_query = """
            SELECT status FROM tracking
            WHERE taskid = %s AND studentid = %s AND teacherid = %s
        """
            cursor.execute(check_entry_query, (taskid, studentid, teacherid))
            status = cursor.fetchone()[0]
            if status == "completed":
                return jsonify({'message': 'task is already submitted'}), 400
            else:
                update_query = """
                UPDATE tracking
                SET status = %s
                WHERE taskid = %s AND studentid = %s AND teacherid = %s
                """
                cursor.execute(update_query, (data['status'], taskid, data['studentid'], teacherid))
                print(data['status'], taskid, data['studentid'], teacherid)
                connection.commit()
                return jsonify({'message': 'status updated'}), 400
 
        else:
            insert_query = """
                INSERT INTO tracking (status, teacherid, studentid, taskid)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                status,
                teacherid,
                studentid,
                taskid,
            ))
            connection.commit()
            return jsonify({'message': 'Task progress submitted successfully'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500