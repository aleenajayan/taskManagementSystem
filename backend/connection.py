

import psycopg2
from psycopg2 import sql
import bcrypt


db_params={
    'host':'localhost',
    'user':'postgres',
    'password':'snehakukku',
    'database':'taskManagement',

}

# Connect to PostgreSQL database
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()


def encrypt_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')


from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from urllib.parse import urlparse, parse_qs

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