
from config import *
from utils.encryptions import *
from flask import Flask, jsonify, request , session
import psycopg2
from flask_cors import CORS
from utils.response import *


#app = Flask(__name__)
import os
import sys
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
# CORS(app)
# from app import app
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})



# Connect to PostgreSQL database
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()

def login():
    try:
        data = request.json
        # u = data.get('username')
        # tid = data.get("teacherid")
        username = data.get('username')
        password = data.get('password')
        print('hello')

        # Query the teacher table
        cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
        login = cursor.fetchone()
        user_type = login[3]
        psw = login[1]
        print("________________",psw)


        if login and bcrypt.checkpw(password.encode('utf-8'), login[1].encode('utf-8')):
            if user_type == "student":
                loginid =login[0]
                cursor.execute("SELECT * FROM student WHERE loginid = %s", (loginid,))
                student = cursor.fetchone()
                if student:
                    sid = student[0]
                    session['sid'] = sid
                    print(session.get('sid'))
                    print("________________sid__________________",sid)
                    response = generate_response({"success": "Student Login successful!"},200)
                    return response


                    return jsonify({'message': 'Student Login successful!'})
            else:
                loginid =login[0]
                cursor.execute("SELECT * FROM teacher WHERE loginid = %s", (loginid,))
                teacher = cursor.fetchone()
                tid = teacher[0]
                session['tid'] = tid
                print("________________tid_________________",tid)
                # return jsonify({'message': 'teacher Login successful!'})
                response = generate_response({"tid": tid},200)
                #response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
                # response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"  # Replace with your allowed origin
                return response
        else:
        
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500




