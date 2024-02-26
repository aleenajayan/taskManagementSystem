from services.teacher import *
from flask import Blueprint


teacher_router= Blueprint('teacher',__name__,url_prefix='/api')


@teacher_router.route('/teacherdashboard/', methods=['GET'])
def teacherdasboard():
    return teacherProfile()
#Add and view Students by teachers
@teacher_router.route('/students/', methods=['POST', 'GET'])
def students():
    return manage_students()
#Add and view Announcements
@teacher_router.route('/announcements/', methods=['POST', 'GET'])
def announcements():
    return manage_announcements()

#Add task by teachers
@teacher_router.route('/tasks/', methods=['POST', 'GET'])# need to change code error while running without giving file
def task():
    return add_task()
#view submitted task
@teacher_router.route('/taskSubmitted/', methods=['GET'])
def taskSubmitted():
    return view_submitted_task()
#Add score
@teacher_router.route('/marks/', methods=['PUT'])
def marks():
    return add_marks()
#Delete student
@teacher_router.route('/deleteStudent/', methods=['DELETE'])
def deleteStudent():
    return delete_student()
#task delete
@teacher_router.route('/deletingTask/', methods=['DELETE']) #need to change the code :violates foreign key constraint 
def Taskdelete():
    return deleteTask()
#view status of task
@teacher_router.route('/progress/', methods=['GET'])
def progress():
    return taskProgress()

@teacher_router.route('/viewmarks/', methods=['GET'])
def marksview():
    return view_marks()

