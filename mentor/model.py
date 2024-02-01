from flask import Flask, jsonify, request , session
import psycopg2

from psycopg2 import sql
# import bcrypt
from connection import *
from cerberus import Validator
    
    
def validate_student_data(data):
    if 'username' not in data or not data['username']:
        return jsonify({'error': 'Username is required'})

    if 'password' not in data or not data['password']:
        return jsonify({'error': 'Password is required'})

    if 'name' not in data or not data['name']:
        return jsonify({'error': 'Name is required'})

    if 'department' not in data or not data['department']:
        return jsonify({'error': 'Department is required'})

    if 'email' not in data or not data['email']:
        return jsonify({'error': 'Email is required'})

    # You can add more specific validation checks for email format, phone number, etc.
    # For example, check if the email is in a valid format
    if '@' not in data['email']:
        return jsonify({'error': 'Invalid email format'})
    if '.' not in data['email']:
        return jsonify({'error': 'Invalid email format'})

    if 'phoneno' not in data or not data['phoneno']:
        return jsonify({'error': 'Phone number is required'})

    # You can add more specific validation checks for phone number format
    if not data['phoneno'].isdigit():
        return jsonify({'error': 'Invalid phone number format'})

    if 'rollNo' not in data or not data['rollNo']:
        return jsonify({'error': 'Roll number is required'})

    if 'classNo' not in data or not data['classNo']:
        return jsonify({'error': 'Class number is required'})

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

def add_task(teacherid):
    if request.method == 'POST':
        try:
            data = request.get_json()

            if 'duedate' not in data:
                return jsonify({'error': 'duedate is a required fields'}), 400
            if 'question' not in data :
                return jsonify({'error': 'question is a required fields'}), 400
            if 'classNo' not in data:
                return jsonify({'error': 'classNo is a required fields'}), 400

            if not data['duedate'] or not data['question'] or not data['classNo']:
                return jsonify({'error': 'All fields must have non-empty values'}), 400

        
            if len(data['question']) > 255:
                return jsonify({'error': 'Question cannot exceed 255 characters'}), 400

            if not data['classNo'].isdigit() or int(data['classNo']) <= 0:
                return jsonify({'error': 'classNo must be a positive integer'}), 400

            insert_query = """
            INSERT INTO task(duedate, question, classNo, teacherid)
            VALUES (%(duedate)s, %(question)s, %(classNo)s, %(teacherid)s);
            """
            cursor.execute(insert_query, {
                'duedate': data['duedate'],
                'question': data['question'],
                'classNo': data['classNo'],
                'teacherid': teacherid
            })

            connection.commit()

            return jsonify({'message': 'Task added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            # Example query, modify as per your needs
            select_query = """
            SELECT * FROM task WHERE teacherid = %s;
            """
            cursor.execute(select_query, (teacherid,))
            tasks = cursor.fetchall()

            # Convert result to a list of dictionaries
            task_list = [{'duedate': row[0], 'question': row[1], 'classNo': row[2], 'teacherid': row[3]} for row in tasks]

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