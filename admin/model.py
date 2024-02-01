from flask import Flask, jsonify, request , session
# from flask_sqlalchemy import SQLAlchemy
import psycopg2

# from flask_bcrypt import Bcrypt, check_password_hash
# import os
from psycopg2 import sql
import bcrypt
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
from connection import *


def encrypt_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')


def manage_teachers():
    if request.method == 'POST':
        try:
            data = request.get_json()
            password = data.get('password')

            # Hash the password
            hashed_password = encrypt_password(password)
            print("___________________",hashed_password)
            # Insert into login table
            login_insert_query = """
            INSERT INTO login (password, username, type)
            VALUES (%(password)s, %(username)s, %(type)s)
            RETURNING loginId
            """
            cursor.execute(login_insert_query, {
                'password': hashed_password,
                'username': data['username'],
                'type': 'teacher'  # Assuming type should be 'teacher' for teacher login
            })
            login_id = cursor.fetchone()[0]  # Get the last insert ID from login table
            print("__________****_________")

            # Insert into teacher table
            teacher_insert_query = """
            INSERT INTO teacher (loginId, name, department, email, phoneNo)
            VALUES (%(loginId)s, %(name)s, %(department)s, %(email)s, %(phoneNo)s)
            """
            cursor.execute(teacher_insert_query, {
                'loginId': login_id,
                'name': data['name'],
                'department': data['department'],
                'email': data['email'],
                'phoneNo': data['phoneNo'],
            })

            # Commit changes and close connection
            connection.commit()

            return jsonify({'message': 'Teacher added successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)})

    elif request.method == 'GET':
        # Retrieve all teachers (you need to implement the query accordingly)
        try:
            select_all_teachers_query = """
            SELECT * FROM teacher
            """
            cursor.execute(select_all_teachers_query)
            teachers = cursor.fetchall()
            # cursor.close()
            # connection.close()

            return jsonify({'teachers': teachers})

        except Exception as e:
            return jsonify({'error': str(e)})
