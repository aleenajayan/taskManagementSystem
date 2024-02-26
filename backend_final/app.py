from flask import Flask, jsonify, request , session
from flask_session import Session
# import psycopg2
from psycopg2 import sql
from flask_cors import CORS


app=Flask(__name__)
CORS(app) 
# CORS(app, origins=['http://localhost:3000'])
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app, supports_credentials=True)  # Ensure supports_credentials is set to True
app.secret_key = 'Task'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
 
server_session = Session(app)

from routes.admin import admin_router
from routes.teacher import teacher_router
from routes.login import login_router


app.register_blueprint(admin_router)
app.register_blueprint(teacher_router)
app.register_blueprint(login_router)


 # Enable CORS for all routes



if __name__ == '__main__':
    app.run(debug=True,port=5001)
