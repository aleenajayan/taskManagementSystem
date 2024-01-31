from flask import Flask, jsonify, request , session
# from flask_sqlalchemy import SQLAlchemy
import psycopg2
import bcrypt
# from flask_bcrypt import Bcrypt, check_password_hash
# import os
from psycopg2 import sql

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


app = Flask(__name__)
app.config['SECRET_KEY'] = 'task'
