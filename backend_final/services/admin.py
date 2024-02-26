from flask import Flask, jsonify, request , session
import psycopg2
from config import *
from utils.validation import *
from utils.encryptions import *
from utils.response import *

# Connect to PostgreSQL database
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()



def manage_teachers():
    if request.method == 'POST':
        try:
            data = request.get_json()
 
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'})

            if not validate_username(data['username']):
                return jsonify({'error': 'Invalid username.username contains only alphanumeric characters'})

            if not validate_phoneno(data['phoneno']):
                return jsonify({'error': 'Invalid phone number'})
            
            if 'password' not in data or not data['password'].strip():
                 return jsonify({'error': 'Password is required and cannot be empty or contain only spaces'})
             
             
            check_email_query = """
            SELECT loginid FROM login WHERE email = %s;
            """
            cursor.execute(check_email_query, (data['email'],))
            existing_login_id = cursor.fetchone()
 
            if existing_login_id:
                return generate_response({'error': 'teacher already exists.'},409)

 
            password = data.get('password')
            hashed_password = encrypt_password(password)
 
            login_insert_query = """
            INSERT INTO login (password, username, type, email)
            VALUES (%(password)s, %(username)s, %(type)s, %(email)s)
            RETURNING loginId
            """
            cursor.execute(login_insert_query, {
                'password': hashed_password,
                'username': data['username'],
                'email': data['email'],
                'type': 'teacher'
            })
            login_id = cursor.fetchone()[0]  
 
            teacher_insert_query = """
            INSERT INTO teacher (loginid, name, department, phoneno)
            VALUES (%(loginid)s, %(name)s, %(department)s, %(phoneno)s)
            """
            cursor.execute(teacher_insert_query, {
                'loginid': login_id,
                'name': data['name'],
                'department': data['department'],
                'phoneno': data['phoneno'],
            })
            connection.commit()
 
            return generate_response({'success': 'Teacher added successfully!'},200)
        except Exception as e:
            return generate_response({'error': str(e)})
 
    elif request.method == 'GET':
        try:
            select_all_teachers_query = """
            SELECT name, department, phoneno FROM teacher
            """
            cursor.execute(select_all_teachers_query)
            teachers = cursor.fetchall()
            output = [
            {
                'name': teacher[0],
                'department': teacher[1],
                'phoneno': teacher[2]
            }
            for teacher in teachers
        ]
 
            return generate_response(output)
 
        except Exception as e:
            return generate_response({'error': str(e)},400)