from services.login import *
from flask import Blueprint
# from flask_cors import CORS
# app = Flask(__name__)
# CORS(app)

login_router= Blueprint('login',__name__,url_prefix='/api')






@login_router.route('/login/', methods=['POST'])
def userlogin():
    return login()