from config import *
from flask import Flask, jsonify, request , session
# import psycopg2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from urllib.parse import urlparse, parse_qs
# from datetime import datetime


drive_credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive.file'])

def upload_to_google_drive(file_path, file_name, folder_id):
    try:
        drive_service = build('drive', 'v3', credentials=drive_credentials)
 
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]  
        }
        media = MediaFileUpload(file_path, mimetype='application/octet-stream')
 
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webContentLink'
        ).execute()
 
        return file.get('webContentLink')
    except Exception as e:
        return str(e)

def extract_file_id(file_url):
    parsed_url = urlparse(file_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('id', [None])[0]
 
def delete_file(file_id):
    try:
        # Build the Google Drive API service
        drive_service = build('drive', 'v3', credentials=drive_credentials)
        # Delete the file by ID
        drive_service.files().delete(fileId=file_id).execute() 
        return {'message': 'File deleted successfully'}
 
    except Exception as e:
        return {'error': str(e)}