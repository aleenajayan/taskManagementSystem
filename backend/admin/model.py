from flask import Flask, jsonify, request , session
import psycopg2
from psycopg2 import sql
import bcrypt
from connection import *
import re


def encrypt_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')

def validate_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+$', email))
 
def validate_username(username):
    return username.isalnum()
 
def validate_phoneno(phoneno):
    return bool(re.match(r'^\d{10}$', phoneno))
 
def validate_name(name):
    return bool(re.match(r'^[a-zA-Z\s]+$', name))
 
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
                return jsonify({'error': 'teacher already exists.'})

 
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
 
            return jsonify({'message': 'Teacher added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)})
 
    elif request.method == 'GET':
        try:
            select_all_teachers_query = """
            SELECT name, department, phoneno FROM teacher
            """
            cursor.execute(select_all_teachers_query)
            teachers = cursor.fetchall()
 
            return jsonify({'teachers': teachers})
 
        except Exception as e:
            return jsonify({'error': str(e)})