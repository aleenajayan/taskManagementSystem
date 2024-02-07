from flask import Flask, jsonify, request , session
import psycopg2

from psycopg2 import sql
# import bcrypt
from connection import *
from cerberus import Validator
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

def validate_student_data(data):
    if 'username' not in data or not data['username'].strip():
        return jsonify({'error': 'Username is required and cannot be empty or contain only spaces'})

    if 'password' not in data or not data['password'].strip():
        return jsonify({'error': 'Password is required and cannot be empty or contain only spaces'})

    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Name is required and cannot be empty or contain only spaces'})

    if 'department' not in data or not data['department'].strip():
        return jsonify({'error': 'Department is required and cannot be empty or contain only spaces'})

    if 'email' not in data or not data['email'].strip():
        return jsonify({'error': 'Email is required and cannot be empty or contain only spaces'})

    # You can add more specific validation checks for email format, phone number, etc.
    # For example, check if the email is in a valid format
    if '@' not in data['email'] or '.' not in data['email']:
        return jsonify({'error': 'Invalid email format'})

    if 'phoneno' not in data or not data['phoneno'].strip():
        return jsonify({'error': 'Phone number is required and cannot be empty or contain only spaces'})

    # You can add more specific validation checks for phone number format
    if not data['phoneno'].strip().isdigit():
        return jsonify({'error': 'Invalid phone number format'})

    if 'rollno' not in data or not data['rollno'].strip():
        return jsonify({'error': 'Roll number is required and cannot be empty or contain only spaces'})

    if 'classno' not in data or not data['classno'].strip():
        return jsonify({'error': 'Class number is required and cannot be empty or contain only spaces'})

    return None  # Indicates successful validation


def validate_student_data(data):
    if 'username' not in data or not data['username'].strip():
        return jsonify({'error': 'Username is required and cannot be empty or contain only spaces'})
 
    if 'password' not in data or not data['password'].strip():
        return jsonify({'error': 'Password is required and cannot be empty or contain only spaces'})
 
    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Name is required and cannot be empty or contain only spaces'})
 
    if 'department' not in data or not data['department'].strip():
        return jsonify({'error': 'Department is required and cannot be empty or contain only spaces'})
 
    if 'email' not in data or not data['email'].strip():
        return jsonify({'error': 'Email is required and cannot be empty or contain only spaces'})
 
    # Check if the email is in a valid format
    if '@' not in data['email'] or '.' not in data['email']:
        return jsonify({'error': 'Invalid email format'})
 
    if 'phoneno' not in data or not data['phoneno'].strip():
        return jsonify({'error': 'Phone number is required and cannot be empty or contain only spaces'})
 
    # Check if the phone number is exactly 10 digits
    if not data['phoneno'].strip().isdigit() or len(data['phoneno'].strip()) != 10:
        return jsonify({'error': 'Invalid phone number format'})
 
    if 'rollno' not in data or not data['rollno'].strip():
        return jsonify({'error': 'Roll number is required and cannot be empty or contain only spaces'})
    
    if 'classno' not in data or not data['classno'].strip():
        return jsonify({'error': 'Class number is required and cannot be empty or contain only spaces'})
 
    # Check if 'classno' is composed of digits and is less than or equal to 13
    if not data['classno'].strip().isdigit() or int(data['classno'].strip()) > 12:
        return jsonify({'error': 'Invalid class number'})
    return None  # Indicates successful validation
 
 
def manage_students(teacherid):
    if request.method == 'POST':
        try:
            data = request.get_json()
 
            # Validate input data
            validation_result = validate_student_data(data)
            if validation_result:
                return validation_result
 
            # Check if email already exists in the login table
            check_email_query = """
            SELECT loginid FROM login WHERE email = %s;
            """
            cursor.execute(check_email_query, (data['email'],))
            existing_login_id = cursor.fetchone()
 
            if existing_login_id:
                return jsonify({'error': 'student already exists.'})
 
            # Extract password from the request data
            password = data.get('password')
 
            # Encrypt the password before storing it
            hashed_password = encrypt_password(password)
 
            # Insert into login table
            login_insert_query = """
            INSERT INTO login (password, username, type, email)
            VALUES (%(password)s, %(username)s, %(type)s, %(email)s)
            RETURNING loginId
            """
            cursor.execute(login_insert_query, {
                'password': hashed_password,
                'username': data['username'],
                'email': data['email'],
                'type': 'student'  # Assuming type should be 'student' for student login
            })
            login_id = cursor.fetchone()[0]  # Get the last insert ID from login table
 
            # Insert into student table
            student_insert_query = """
            INSERT INTO student (loginid, name, department, phoneno, rollno, classno, teacherid)
            VALUES (%(loginid)s, %(name)s, %(department)s, %(phoneno)s, %(rollno)s, %(classno)s, %(teacherid)s)
            """
            cursor.execute(student_insert_query, {
                'loginid': login_id,
                'name': data['name'],
                'department': data['department'],
                'phoneno': data['phoneno'],
                'rollno': data['rollno'],
                'classno': data['classno'],
                'teacherid': teacherid
            })
 
            # Commit changes and close connection
            connection.commit()
 
            return jsonify({'message': 'Student added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)})
 
    elif request.method == 'GET':
        try:
            # Retrieve students by teacherId
            teacher_id = teacherid
            if teacher_id is not None:
                # Example query, modify as per your needs
                select_query = """
                SELECT * FROM student WHERE teacherId = %s;
                """
                cursor.execute(select_query, (teacher_id,))
                students = cursor.fetchall()
 
                return jsonify({'students': students})
            else:
                return jsonify({'error': 'Please provide a valid teacherId in the query parameter'})
        except Exception as e:
            return jsonify({'error': str(e)})
#_________________________________________________________________
def manage_announcements(teacherid):
    if request.method == 'POST':
        try:
            data = request.get_json()
 
            # Validate required fields and non-empty values
            if 'announcement' not in data or 'classno' not in data:
                return jsonify({'error': 'Announcement and classno are required fields and must have non-empty values'}), 400
 
            if not data['announcement'].strip() or not data['classno'].strip():
                return jsonify({'error': 'Announcement and classNo must have non-empty values'}), 400
 
            # Individual validation for announcement
            if len(data['announcement'].strip()) > 255 or not data['announcement'].strip():
                return jsonify({'error': 'Invalid announcement format or length > 255'}), 400
 
            # Individual validation for classNo
            if not data['classno'].isdigit() or int(data['classno']) <= 0 or int(data['classno']) >= 13:
                return jsonify({'error': 'Invalid classno. It must be a positive integer less than 13'}), 400
 
            insert_query = """
            INSERT INTO announcement(announcement, classno, teacherid)
            VALUES (%(announcement)s, %(classno)s, %(teacherid)s);
            """
            cursor.execute(insert_query, {
                'announcement': data['announcement'],
                'classno': data['classno'],
                'teacherid': teacherid
            })
 
            connection.commit()
            return jsonify({'message': 'Announcement added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            if teacherid:
                select_query = """
                SELECT announcement.announcement, teacher.name
                FROM announcement
                JOIN teacher ON announcement.teacherid = teacher.teacherid
                WHERE announcement.classno = %s OR announcement.classno = 'all'
                """
                cursor.execute(select_query, (teacherid,))
                announcements = cursor.fetchall()
 
                return jsonify({'announcements': announcements})
            else:
                return jsonify({'error': 'Please provide a valid teacherId in the URL'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
 
#__________________________________________________________________________
# drive_credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive.file'])
def add_task(teacherid):
    if request.method == 'POST':
        try:
            file = request.files['file']
            print("______________________________________",file)
            file.save('temp_file')
            duedate = request.form['duedate']
            question = request.form['question']
            classno = request.form['classno']
            folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'
            
            check_existing_query = """
            SELECT COUNT(*)
            FROM task
            WHERE duedate = %s AND teacherid = %s AND question = %s AND classno=%s;
            """
            cursor.execute(check_existing_query, (duedate, teacherid, question, classno))
            existing_count = cursor.fetchone()[0] 
            
            if existing_count > 0:
                return jsonify({'error': 'Task already exists for this task.'})
                    
            if not classno.isdigit() or int(classno) <= 0 or int(classno) >= 13:
                return jsonify({'error': 'Invalid classno. It must be a positive integer less than 13'}), 400
 
            
            if not duedate:
                return jsonify({'error': 'Due date is required.'}), 400

            if not question and not file:
                return jsonify({'error': 'Either "question" or "file" is required.'}), 400

            if not classno:
                return jsonify({'error': 'Class number is required.'}), 400

            file_url = upload_to_google_drive('temp_file', file.filename, folder_id)
            print("___________________",file_url)

            insert_query = """
            INSERT INTO task(duedate, question, classno, teacherid,file)
            VALUES (%(duedate)s, %(question)s, %(classno)s, %(teacherid)s,%(file)s);
            """
            if file and question:
                cursor.execute(insert_query, {
                    'duedate': duedate,
                    'question': question,
                    'classno': classno,
                    'teacherid': teacherid,
                    'file': file_url
                })

                connection.commit()
                return jsonify({'message': 'Task added successfully!'})

            elif file and not question:
                cursor.execute(insert_query, {
                    'duedate': duedate,
                    'question': "Nill",
                    'classno': classno,
                    'teacherid': teacherid,
                    'file': file_url
                })

                connection.commit()
                return jsonify({'message': 'Task added successfully!'})
            else:
                cursor.execute(insert_query, {
                    'duedate': duedate,
                    'question': question,
                    'classno': classno,
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
            task_list = [{'duedate': row[2], 'question': row[3], 'classno': row[4],'file': row[5] } for row in tasks]

            return jsonify({'tasks': task_list})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
 
def deleteTask(taskid):
    try:
        fetch_url_query = """
        SELECT file FROM task WHERE taskid = %s;
        """
        cursor.execute(fetch_url_query, (taskid,))
        existing_file_url = cursor.fetchone()
 
        if existing_file_url:
            existing_file_id = extract_file_id(existing_file_url[0])
 
            if existing_file_id:
                result = delete_file(existing_file_id)
                print(result)
            else:
                print("Unable to extract file ID from the existing URL.")
        
        
        # Fetch file URLs for the task from the tasksubmission table
        fetch_submission_urls_query = """
        SELECT file FROM tasksubmission WHERE taskid = %s;
        """
        cursor.execute(fetch_submission_urls_query, (taskid,))
        submission_urls = cursor.fetchall()
 
        # Iterate through submission URLs and delete each file from Google Drive
        for submission_url in submission_urls:
            file_id = extract_file_id(submission_url[0])
            if file_id:
                delete_file(file_id)
 
        # Delete rows from the tasksubmission table
        delete_tasksubmission_query = """
            DELETE FROM tasksubmission
            WHERE taskid = %s;
        """
        cursor.execute(delete_tasksubmission_query, (taskid,))
        connection.commit()
 
        # Delete the task from the task table
        delete_task_query = """
            DELETE FROM task
            WHERE taskid = %s;
        """
        cursor.execute(delete_task_query, (taskid,))
        connection.commit()
 
        return {'message': 'Task and associated files deleted successfully'}
 
    except Exception as e:
        return {'error': str(e)}, 500

def view_submitted_task(teacherid):
    try:
        select_query = """
        SELECT ts.file, ts.classno, ts.score, s.name as student_name
        FROM tasksubmission ts
        JOIN student s ON ts.studentid = s.studentid
        WHERE ts.teacherid = %s;
        """
        cursor.execute(select_query, (teacherid,))
        tasksubmissions = cursor.fetchall()

        tasksubmissions_data = [
            {
                'file': tasksubmission[0],
                'classno': tasksubmission[1],
                'score':tasksubmission[2],
                'student_name': tasksubmission[3],
            }
            for tasksubmission in tasksubmissions
        ]
        return jsonify({'tasksubmissions': tasksubmissions_data})
    except Exception as e:
        return jsonify({'error': str(e)})


def add_marks(submissionid):
    try:
        data = request.get_json()
 
        # Validate score field
        if 'score' not in data or str(data['score']).strip() == '':
            return jsonify({'error': 'Score is a required field and cannot be empty'}), 400
 
        # Validate score is a number
        if not str(data['score']).replace('.', '', 1).isdigit():
            return jsonify({'error': 'Score must be a numeric value'}), 400
 
        # Convert score to an integer
        score = int(float(data['score']))  # Convert to float first to handle decimal values
 
        if score > 50:
            return jsonify({'error': 'Score cannot be greater than 50'}), 400
 
        cursor.execute("UPDATE taskSubmission SET score = %s WHERE submissionid = %s", (score, submissionid))
        connection.commit()
 
        return jsonify({'message': 'Marks updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def delete_student(studentid):
    try:
        check_student_query = "SELECT * FROM student WHERE studentid = %s;"
        cursor.execute(check_student_query, (studentid,))
        existing_student = cursor.fetchone()

        if not existing_student:
            return jsonify({'error': f'Student with studentid {studentid} does not exist'}), 404

        # Delete Student from Task Submissions table
        delete_task_submissions_query = "DELETE FROM tasksubmission WHERE studentid = %s;"
        cursor.execute(delete_task_submissions_query, (studentid,))

        # Delete the Student from student table
        delete_student_query = "DELETE FROM student WHERE studentid = %s;"
        cursor.execute(delete_student_query, (studentid,))

        connection.commit()

        return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        # Handle exceptions appropriately
        print(f"Error: {e}")
        connection.rollback()
        return jsonify({'error': str(e)}), 500



def taskProgress(taskid):
    try:
        print("_____________try____________")
        select_query = """
        SELECT t.status ,st.name
        FROM tracking t
        JOIN student st ON t.studentid = st.studentid
        WHERE t.taskid = %s;
        """
        cursor.execute(select_query, (taskid,))
        tasks = cursor.fetchall()
        print("_____________tTASK____________",tasks)
 
        progress_data = [
            {
                'status': task[0],
                'student name': task[1]
                # 'teachername': task[2]
            }
            for task in tasks
        ]
 
        return jsonify({'tasks': progress_data})
    except Exception as e:
        return jsonify({'error': str(e)})

# def resetRequest():
#     data = request.get_json()
 
#     recipient = data['recipient']
#     subject = data['subject']
#     message_body = data['message_body']
#     print("______collected data__________________")
 
#     try:
#         message = Message(subject, recipients=[recipient])
#         print("_____________message___________",message)
#         message.body = message_body
#         mail.send(message)
#         return jsonify({'message': 'Email sent successfully!'})
 
#         # flash('Email sent successfully', 'success')
#     except Exception as e:
#         return jsonify(f'Error sending email: {str(e)}', 'error')
 
#     return redirect(url_for('index'))

