from connection import *
from flask import Flask
import psycopg2 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from model import *

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'task'
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()


#____________________________________View Task by Student_______________________________________________
   
@app.route('/api/student/task/<string:classno>', methods=['GET'])
def task(classno):
    return view_task(classno)
    
#_____________________________view Announcement by students______________________________________________
@app.route('/api/student/announcement/<string:classno>', methods=['GET'])
def announcement(classno):
    return view_announcement(classno)

#________________________________Task submission by students_________________________________________________
 
@app.route('/api/student/task/submit/<string:taskid>', methods=['POST'])
def submit_task(taskid):
    return task_submission(taskid)

#________________________________update submitted task by students_____________________________________________

@app.route('/api/student/task/update/<string:submissionid>', methods=['PUT'])
def update_task(submissionid):
    return task_updation(submissionid)

#________________________________delete submitted task by students_____________________________________________

@app.route('/api/student/task/delete/<string:submissionid>', methods=['DELETE'])
def delete_task(submissionid):
    return task_deletion(submissionid)

#_______________________________task priority list____________________________________________________________

@app.route('/api/student/tasklist/<string:studentid>', methods=['GET'])
def task_list(studentid):
    return tasklist_view(studentid)

if __name__ == '__main__':
    app.run(debug=True, port=5001)










# @app.route('/api/update_uploaded_file/<string:submissionid>', methods=['POST'])
# def update_uploaded_file():
#     try:
#         file = request.files['file']
#         file.save('temp_file')
#         classno = request.form['classno']
#         teacherid = request.form['teacherid']
#         studentid = request.form['studentid']
#         taskid = request.form['taskid']
#         submissionid = request.form['submissionid']

#         folder_id = '1UiuN6RWsgLSvBJOFhCHGwyV5f5fOirks'

#         file_url = upload_to_google_drive('temp_file', file.filename, folder_id)
#         update_task_submission_url_in_database(submissionid, file_url, classno, teacherid, studentid, taskid)

#         return jsonify({'message': 'File updated successfully', 'file_url': file_url})
#     except Exception as e:
#         return jsonify({'error': str(e)})
    
# @app.route('/api/add_tasksubmission', methods=['POST'])
# def add_tasksubmission():
#     try:
#         data = request.get_json()

#         insert_query = """
#         INSERT INTO public.tasksubmission(file, score, classno, teacherid, studentid, taskid)
# 	    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
#         """
#         cursor.execute(insert_query, (
#             data['file'],
#             data['score'],
#             data['remarks'],
#             data['doubt'],
#             data['classno'],
#             data['teacherid'],
#             data['studentid'],
#             data['taskid']
#         ))


#         connection.commit()
#         # cursor.close()
#         # connection.close()

#         return jsonify({'message': 'tasksubmission added successfully!'})
#     except Exception as e:
#         connection.rollback()
#         return jsonify({'error': str(e)})
    

