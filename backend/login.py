
from connection import *
from flask import Flask, jsonify, request , session

def login():
    try:
        data = request.json
        # u = data.get('username')
        # tid = data.get("teacherid")
        username = data.get('username')
        password = data.get('password')

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
                    print("________________sid__________________",sid)
                    return jsonify({'message': 'Student Login successful!'})
            else:
                loginid =login[0]
                cursor.execute("SELECT * FROM teacher WHERE loginid = %s", (loginid,))
                teacher = cursor.fetchone()
                tid = teacher[0]
                session['tid'] = tid
                print("________________tid_________________",tid)
                return jsonify({'message': 'teacher Login successful!'})
        else:
        
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500




