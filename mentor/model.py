from flask import Flask, jsonify, request , session
import psycopg2

from psycopg2 import sql
# import bcrypt
from connection import *
from cerberus import Validator
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
app = Flask(__name__)
app.secret_key = 'taskmanagement'
 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tarentotask@gmail.com'
app.config['MAIL_PASSWORD'] = 'xqiu aycu whas eknl'
app.config['MAIL_DEFAULT_SENDER'] = 'tarentotask@gmail.com'
 
mail = Mail(app)
    
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

    if 'rollNo' not in data or not data['rollNo'].strip():
        return jsonify({'error': 'Roll number is required and cannot be empty or contain only spaces'})

    if 'classNo' not in data or not data['classNo'].strip():
        return jsonify({'error': 'Class number is required and cannot be empty or contain only spaces'})

    return None  # Indicates successful validation


def manage_students(teacherid):
    if request.method == 'POST':
        try:
            data = request.json

            # Validate input data
            validation_result = validate_student_data(data)
            if validation_result:
                return validation_result

            # Extract password from the request data
            password = data.get('password')

            # Encrypt the password before storing it
            hashed_password = encrypt_password(password)

            # Insert into login table
            login_insert_query = """
            INSERT INTO login (password, username, type)
            VALUES (%(password)s, %(username)s, %(type)s)
            RETURNING loginId
            """
            cursor.execute(login_insert_query, {
                'password': hashed_password,
                'username': data['username'],
                'type': 'student'  # Assuming type should be 'student' for student login
            })
            login_id = cursor.fetchone()[0]  # Get the last insert ID from login table

            # Insert into student table
            student_insert_query = """
            INSERT INTO student (loginId, name, department, email, phoneno, rollNo, classNo, teacherId)
            VALUES (%(loginId)s, %(name)s, %(department)s, %(email)s, %(phoneno)s, %(rollNo)s, %(classNo)s, %(teacherId)s)
            """
            cursor.execute(student_insert_query, {
                'loginId': login_id,
                'name': data['name'],
                'department': data['department'],
                'email': data['email'],
                'phoneno': data['phoneno'],
                'rollNo': data['rollNo'],
                'classNo': data['classNo'],
                'teacherId': teacherid
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

def manage_announcements(teacherid):
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Validate required fields
            if 'announcement' not in data or 'classNo' not in data:
                print("_______1_________")
                return jsonify({'error': 'Announcement and classNo are required fields'}), 400

            # Validate non-empty values
            if not data['announcement'] or not data['classNo']:
                print("_______2________")

                return jsonify({'error': 'Announcement and classNo must have non-empty values'}), 400

            # Individual validation for announcement
            if len(data['announcement']) > 255:
                print("_______3________")

                return jsonify({'error': 'Announcement cannot exceed 255 characters'}), 400

            # Individual validation for classNo
                print("_______4_________")

            if not data['classNo'].isdigit() or int(data['classNo']) <= 0:
                return jsonify({'error': 'classNo must be a positive integer'}), 400

            insert_query = """
            INSERT INTO announcement(announcement, classno, teacherid)
            VALUES (%(announcement)s, %(classNo)s, %(teacherid)s);
            """
            cursor.execute(insert_query, {
                'announcement': data['announcement'],
                'classNo': data['classNo'],
                'teacherid': teacherid
            })

            connection.commit()
            return jsonify({'message': 'Announcement added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            if teacherid:
                # Example query, modify as per your needs
                select_query = """
                SELECT * FROM announcement WHERE teacherid = %s;
                """
                cursor.execute(select_query, (teacherid,))
                announcements = cursor.fetchall()

                # Convert result to a list of dictionaries
                # announcement_list = [{'announcement': row[1], 'classno': row[2], 'teacherid': row[3]} for row in announcements]

                return jsonify({'announcements': announcements})
            else:
                return jsonify({'error': 'Please provide a valid teacherId in the URL'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

 

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


def view_submitted_task(teacherid):
    try:
        select_query = """
        SELECT ts.file, ts.classNo, s.name as student_name
        FROM tasksubmission ts
        JOIN student s ON ts.studentid = s.studentid
        WHERE ts.teacherid = %s;
        """
        cursor.execute(select_query, (teacherid,))
        tasksubmissions = cursor.fetchall()

        tasksubmissions_data = [
            {
                'file': tasksubmission[0],
                'classNo': tasksubmission[1],
                'student_name': tasksubmission[2],
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
        if 'score' not in data:
            return jsonify({'error': 'score is a required field'}), 400

        # Validate score is a number
        if not isinstance(data['score'], (int, float)):
            return jsonify({'error': 'score must be a numeric value'}), 400

        # Additional validation for specific score range if needed
        # Example: Check if score is within a valid range
        # ...

        score = data['score']

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

