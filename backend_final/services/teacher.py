from flask import Flask, jsonify, request , session
import psycopg2
from config import *
from utils.googleapi import *
from utils.validation import *
from utils.encryptions import *
from flask_cors import CORS


# Connect to PostgreSQL database
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()
def teacherProfile():
    teacherid = request.args.get("teacherid")
    try:
        select_query = """SELECT t.name, t.phoneno, t.department, l.email
        FROM teacher t
        JOIN login l ON t.loginid = l.loginid
        WHERE t.teacherid = %s;
        """
        # """
        # SELECT * FROM teacher WHERE teacherId = %s;
        # """
        cursor.execute(select_query, (teacherid,))
        students = cursor.fetchall()
        output = [
            {
                'name': student[0],
                'department': student[2],
                'phoneno': student[1],
                'email': student[3]
            }
            for student in students
        ]

        return generate_response(output,200)
    except Exception as e:
        return generate_response({'error': str(e)})
     
def manage_students():
    # teacherid = request.args.get("teacherid")
    teacherid = request.args.get("teacherid")

    if request.method == 'POST':
        try:
            data = request.get_json()
 
            # Validate input data
            # validation_result = validate_student_data(data)
            # if validation_result:
                # return generate_response('error': validation_result)
                # return generate_response({ 'error': "gggg" });

 
            # Check if email already exists in the login table
            check_email_query = """
            SELECT loginid FROM login WHERE email = %s;
            """
            cursor.execute(check_email_query, (data['email'],))
            existing_login_id = cursor.fetchone()
            print(existing_login_id)
 
            if existing_login_id:
                return generate_response({'message': 'student already exists.'})
 
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
 
            return generate_response({'success': 'Student added successfully!'},200)
        except Exception as e:
            return generate_response({'error': str(e)})
 
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
                output = [
                    {
                        'name': student[3],
                        'department': student[4],
                        'phoneno': student[5],
                        'rollno': student[7],
                        'classno': student[6],
                        'studentid':student[0]
                    }
                    for student in students
                ]
 
                return generate_response(output,200)
            else:
                return generate_response({'error': 'Please provide a valid teacherId in the query parameter'})
        except Exception as e:
            return generate_response({'error': str(e)})
#_________________________________________________________________
def manage_announcements():
    try:
        if request.method == 'POST':
            announcement = request.form['announcement']
            classno = request.form['classno']
            teacherid = request.form['teacherid']

            insert_query = """
            INSERT INTO announcement(announcement, classno, teacherid)
            VALUES (%(announcement)s, %(classno)s, %(teacherid)s);
            """
            cursor.execute(insert_query, {
                'announcement': announcement,
                'classno': classno,
                'teacherid': teacherid
            })

            connection.commit()
            return jsonify({'message': 'Announcement added successfully!'})
        elif request.method == 'GET':
            teacherid = request.args.get("teacherid")
            
            try:
                if teacherid:
                    select_query = """
                    SELECT announcement.announcement, announcement.classno, teacher.name
                    FROM announcement
                    JOIN teacher ON announcement.teacherid = teacher.teacherid
                    WHERE announcement.teacherid = %s
                    """
                    cursor.execute(select_query, (teacherid,))
                    announcements = cursor.fetchall()
                    output = [
                        {
                            'announcement': announcement[0],
                            'classno': announcement[1],
                            'teachername': announcement[2]
                        }
                        for announcement in announcements
                    ]
                    return generate_response(output)
                else:
                    return jsonify({'error': 'Please provide a valid teacherId in the URL'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 
#__________________________________________________________________________
def add_task():
    teacher = request.args.get("teacherid")
    if request.method == 'POST':
        try:
            file = request.files['file']
            print("______________________________________",file)
            file.save('temp_file')
            duedate = request.form['duedate']
            question = request.form['question']
            classno = request.form['classno']
            teacherid = request.form['teacherid']
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
        teacherid = request.args.get("teacherid")
        
        try:
            select_query = """
            SELECT * FROM task WHERE teacherid = %s;
            """
            cursor.execute(select_query, (teacherid,))
            tasks = cursor.fetchall()
            output=[
                {
                    'duedate': task[2],
                    'question': task[3],
                    'file': task[5],
                    'taskid':task[0]
                }
                for task in tasks
            ]
            # task_list = [{'duedate': row[2], 'question': row[3], 'classno': row[4],'file': row[5] } for row in tasks]

            return generate_response(output,200)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
 
def deleteTask():
    taskid = request.args.get("taskid")
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

def view_submitted_task():
    taskid = request.args.get("taskid")

    try:
        select_query = """
        SELECT ts.file, ts.classno, ts.score, ts.submissionid, s.name as student_name
        FROM tasksubmission ts
        JOIN student s ON ts.studentid = s.studentid
        WHERE ts.taskid = %s AND ts.score= 0;
        """
        cursor.execute(select_query, (taskid,))
        tasksubmissions = cursor.fetchall()

        tasksubmissions_data = [
            {
                'file': tasksubmission[0],
                'classno': tasksubmission[1],
                'score': tasksubmission[2],
                'submissionid':tasksubmission[3],
                'student_name': tasksubmission[4],
            }
            for tasksubmission in tasksubmissions
        ]
        return generate_response(tasksubmissions_data)
    except Exception as e:
        return generate_response({'error': str(e)})

def view_marks():
    taskid = request.args.get("taskid")

    try:
        select_query = """
        SELECT ts.file, ts.classno, ts.score, s.name as student_name
        FROM tasksubmission ts
        JOIN student s ON ts.studentid = s.studentid
        WHERE ts.taskid = %s AND ts.score > 0;
        """
        cursor.execute(select_query, (taskid,))
        tasksubmissions = cursor.fetchall()

        tasksubmissions_data = [
            {
                'file': tasksubmission[0],
                'classno': tasksubmission[1],
                'score': tasksubmission[2],
                'student_name': tasksubmission[3],
            }
            for tasksubmission in tasksubmissions
        ]
        return generate_response(tasksubmissions_data)
    except Exception as e:
        return generate_response({'error': str(e)})

    


def add_marks():
    if request.method == 'PUT':
        try:
            score = request.form['score']
            submissionid = request.form['submissionid']
            # data = request.get_json()
 
            # Validate score field
            # if 'score' not in data or str(data['score']).strip() == '':
            #     return jsonify({'error': 'Score is a required field and cannot be empty'}), 400
 
            # # Validate score is a number
            # if not str(data['score']).replace('.', '', 1).isdigit():
            #     return jsonify({'error': 'Score must be a numeric value'}), 400
 
            # Convert score to an integer
            score = int(float(score))  # Convert to float first to handle decimal values
 
            if score > 50:
                return jsonify({'error': 'Score cannot be greater than 50'}), 400
 
            cursor.execute("UPDATE taskSubmission SET score = %s WHERE submissionid = %s", (score, submissionid))
            connection.commit()
 
            return jsonify({'message': 'Marks updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


def delete_student():
    studentid= request.args.get("studentid")
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



def taskProgress():
    taskid=request.args.get("taskid")
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
                'studentname': task[1]
                # 'teachername': task[2]
            }
            for task in tasks
        ]
 
        return generate_response(progress_data)
    except Exception as e:
        return generate_response({'error': str(e)})

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

