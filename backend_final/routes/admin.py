from services.admin import *
from flask import Blueprint


admin_router= Blueprint('admin',__name__,url_prefix='/api')

@admin_router.route('/teachers/', methods=['POST', 'GET'])
def teachers():
    return manage_teachers()
