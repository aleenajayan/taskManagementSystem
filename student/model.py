from connection import *
from flask import Flask, jsonify, request , session
# import psycopg2
# import bcrypt
# from flask_bcrypt import Bcrypt, check_password_hash
# import os
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

        # Check if task submission already exists for the given studentid, teacherid, and taskid
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

        # Get the due date of the task
        select_due_date_query = "SELECT duedate FROM task WHERE taskid = %s"
        cursor.execute(select_due_date_query, (taskid,))
        due_date = cursor.fetchone()[0]

        # Convert the due date to a datetime object
        due_date = datetime.strptime(str(due_date), "%Y-%m-%d")

        # Check if the current date is past the due date
        current_date = datetime.now()
        if current_date > due_date:
            return jsonify({'error': 'Task submission is past the due date.'})

        # Continue with the submission process

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
        # Build the Google Drive API service
        drive_service = build('drive', 'v3', credentials=drive_credentials)
        # Delete the file by ID
        drive_service.files().delete(fileId=file_id).execute()

        return {'message': 'File deleted successfully'}

    except Exception as e:
        return {'error': str(e)} 
  

def task_updation(submissionid):
    try:
        # Fetch existing file URL from the tasksubmission table
        fetch_url_query = """
        SELECT file FROM tasksubmission WHERE submissionid = %s;
        """
        cursor.execute(fetch_url_query, (submissionid,))
        existing_file_url = cursor.fetchone()

        if not existing_file_url:
            return jsonify({'error': 'No file found for the given submissionid'})

        # Extract file ID from the existing file URL
        existing_file_id = extract_file_id(existing_file_url[0])

        # Delete the existing file from Google Drive
        if existing_file_id:
            result = delete_file(existing_file_id)
            print(result)
        else:
            print("Unable to extract file ID from the existing URL.")

        # Upload the new file to Google Drive
        file = request.files['file']
        file.save('temp_file')
        folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'
        file_url = upload_to_google_drive('temp_file', file.filename, folder_id)

        # Update the tasksubmission table with the new file URL
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
        # Fetch existing file URL from the tasksubmission table
        fetch_url_query = """
        SELECT file FROM tasksubmission WHERE submissionid = %s;
        """
        cursor.execute(fetch_url_query, (submissionid,))
        existing_file_url = cursor.fetchone()

        if not existing_file_url:
            return jsonify({'error': 'No file found for the given submissionid'})

        # Extract file ID from the existing file URL
        existing_file_id = extract_file_id(existing_file_url[0])

        # Delete the existing file from Google Drive
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
        # Fetch the classno from the student table using studentid
        select_classno_query = "SELECT classno FROM student WHERE studentid = %s"
        cursor.execute(select_classno_query, (student_id,))
        classno = cursor.fetchone()

        if not classno:
            return jsonify({'error': 'Student not found'})

        classno = classno[0]

        # Get the current date and time
        current_date = datetime.now()
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

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



#____________________upload file by teacher__________________________
# drive_credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive.file'])
def add_task(teacherid):
    if request.method == 'POST':
        try:
            file = request.files['file']
            print("______________________________________",file)
            file.save('temp_file')
            duedate = request.form['duedate']
            question = request.form['question']
            classNo = request.form['classNo']
            folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'
            
            if not duedate:
                return jsonify({'error': 'Due date is required.'}), 400
 
            if not question and not file:
                return jsonify({'error': 'Either "question" or "file" is required.'}), 400
 
            if not classNo:
                return jsonify({'error': 'Class number is required.'}), 400
 
            file_url = upload_to_google_drive('temp_file', file.filename, folder_id)
            print("___________________",file_url)
 
            insert_query = """
            INSERT INTO task(duedate, question, classNo, teacherid,file)
            VALUES (%(duedate)s, %(question)s, %(classNo)s, %(teacherid)s,%(file)s);
            """
            if file and question:
                cursor.execute(insert_query, {
                    'duedate': duedate,
                    'question': question,
                    'classNo': classNo,
                    'teacherid': teacherid,
                    'file': file_url
                })
 
                connection.commit()
                return jsonify({'message': 'Task added successfully!'})
 
            elif file and not question:
                cursor.execute(insert_query, {
                    'duedate': duedate,
                    'question': "Nill",
                    'classNo': classNo,
                    'teacherid': teacherid,
                    'file': file_url
                })
 
                connection.commit()
                return jsonify({'message': 'Task added successfully!'})
            else:
                cursor.execute(insert_query, {
                    'duedate': duedate,
                    'question': question,
                    'classNo': classNo,
                    'teacherid': teacherid,
                    'file': "Nill"
                })
 
                connection.commit()
                return jsonify({'message': 'Task added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            select_query = """
            SELECT * FROM task WHERE teacherid = %s;
            """
            cursor.execute(select_query, (teacherid,))
            tasks = cursor.fetchall()
            task_list = [{'duedate': row[2], 'question': row[3], 'classNo': row[4], 'teacherid': row[1] ,'file': row[5] } for row in tasks]
 
            return jsonify({'tasks': task_list})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
 
#_____________________________________________delete task by teacher______________________________________
def updateTask(taskid):
    try:
        # Fetch the existing task data
        cursor.execute('SELECT * FROM task WHERE taskid = %s', (taskid,))
        task = cursor.fetchone()
 
        if task is None:
            return jsonify({'message': 'Task not found'}), 404
 
        # Check if the request contains form data
        if request.form:
            form_data_dict = dict(request.form)
 
            # If 'file' is present in form data, handle file update
            if 'file' in form_data_dict:
                existing_file_id = extract_file_id(task[5])
 
                # Delete the existing file from Google Drive
                if existing_file_id:
                    result = delete_file(existing_file_id)
                    print("_______deleted__________",result)
 
                # Upload the new file to Google Drive
                file = request.files['file']
                file.save('temp_file')
                folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'
                file_url = upload_to_google_drive('temp_file', file.filename, folder_id)
 
                # Update the task table with the new file URLS
                form_data_dict['file'] = file_url
                
 
            # Update other fields
            updated_fields = []
            for key, value in form_data_dict.items():
                cursor.execute(f'UPDATE task SET {key} = %s WHERE taskid = %s', (value, taskid))
                updated_fields.append(key)
 
            connection.commit()
            return jsonify({'message': 'Task data updated successfully', 'updated_fields': updated_fields})
 
        # If no form data is present in the request
        else:
            return jsonify({'message': 'No data provided in the request'}), 400
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# #_________________________________mail send by type_______________
# def send_email():
#     try:
#         # Collect data from the request JSON
#         data = request.get_json()
#         student_email = data['student_email']
#         subject = data['subject']
#         body = data['message_body']
#         user_type = data['type']  # Assuming 'type' is the parameter indicating the user type

#         # Fetch all emails based on the user type from the login table
#         fetch_emails_query = "SELECT email FROM login WHERE type = %s"
#         cursor.execute(fetch_emails_query, (user_type,))
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

#         return jsonify({'message': 'Emails sent successfully'})
#     except Exception as e:
#         return jsonify({'error': str(e)})

# def tasklist_view(student_id):
#     try:
#         # Fetch the classno from the student table using studentid
#         select_classno_query = "SELECT classno FROM student WHERE studentid = %s"
#         cursor.execute(select_classno_query, (student_id,))
#         classno = cursor.fetchone()

#         if not classno:
#             return jsonify({'error': 'Student not found'})

#         classno = classno[0]

#         # Get the current date and time
#         current_date = datetime.now()

#         # Query to fetch tasks excluding those already submitted by the student
#         select_query = """
#         SELECT t.duedate, t.question, te.name
#         FROM task t
#         JOIN teacher te ON t.teacherid = te.teacherid
#         WHERE t.classno = %s
#         AND t.duedate >= %s
#         AND NOT EXISTS (
#             SELECT 1
#             FROM tasksubmission ts
#             WHERE ts.taskid = t.taskid
#             AND ts.studentid = %s
#         );
#         """
#         cursor.execute(select_query, (classno, current_date, student_id))
#         tasks = cursor.fetchall()

#         tasks_data = [
#             {
#                 'duedate': task[0],
#                 'question': task[1],
#                 'teachername': task[2]
#             }
#             for task in tasks
#         ]

#         return jsonify({'tasks': tasks_data})
#     except Exception as e:
#         return jsonify({'error': str(e)})