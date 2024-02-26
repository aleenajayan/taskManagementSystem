import re
from flask import Flask, jsonify, request , session


def validate_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+$', email))
 
def validate_username(username):
    return username.isalnum()
 
def validate_phoneno(phoneno):
    return bool(re.match(r'^\d{10}$', phoneno))
 
def validate_name(name):
    return bool(re.match(r'^[a-zA-Z\s]+$', name))

def validate_student_data(data):
    if 'username' not in data or not data['username'].strip():
        return jsonify({'error': 'Username is required and cannot be empty or contain only spaces'})
 
    if 'password' not in data or not data['password'].strip():
        return jsonify({'error': 'Password is required and cannot be empty or contain only spaces'})
 
    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Name is required and cannot be empty or contain only spaces'})
 
    if 'department' not in data or not data['department'].strip():
        return jsonify({'error': 'Department is required and cannot be empty or contain only spaces'})
 
    if 'email' not in data or not data['email'].strip():
        return jsonify({'error': 'Email is required and cannot be empty or contain only spaces'})
 
    # Check if the email is in a valid format
    if '@' not in data['email'] or '.' not in data['email']:
        return jsonify({'error': 'Invalid email format'})
 
    if 'phoneno' not in data or not data['phoneno'].strip():
        return jsonify({'error': 'Phone number is required and cannot be empty or contain only spaces'})
 
    # Check if the phone number is exactly 10 digits
    if not data['phoneno'].strip().isdigit() or len(data['phoneno'].strip()) != 10:
        return jsonify({'error': 'Invalid phone number format'})
 
    if 'rollno' not in data or not data['rollno'].strip():
        return jsonify({'error': 'Roll number is required and cannot be empty or contain only spaces'})
    
    if 'classno' not in data or not data['classno'].strip():
        return jsonify({'error': 'Class number is required and cannot be empty or contain only spaces'})
 
    # Check if 'classno' is composed of digits and is less than or equal to 13
    if not data['classno'].strip().isdigit() or int(data['classno'].strip()) > 12:
        return jsonify({'error': 'Invalid class number'})
    return None  # Indicates successful validation
 


 
def generate_response(response=None, status_code=200):
 
    success_status_codes = [200, 201, 204, 206, 301, 302, 304, 307, 308]  # Successful responses
    client_error_status_codes = [400, 401, 403, 404, 405, 408, 409, 410, 413, 414, 415, 429]  # Client errors
    server_error_status_codes = [500, 501, 502, 503, 504, 505]  # Server errors
 
    if status_code in success_status_codes:
        status = 'success'
        message = get_success_message(status_code)
        error = None
    elif status_code in client_error_status_codes:
        status = 'client_error'
        message = None
        error = get_client_error_message(status_code)
    elif status_code in server_error_status_codes:
        status = 'server_error'
        message = None
        error = get_server_error_message(status_code)
    else:
        status = 'unknown'
        message = None
        error = 'Unknown error'
 
    response_data = {
        'response': response,
        'message': message,
        'error': error,
        'status': status,
        'status code': status_code
    }
 
    return jsonify(response_data)
 
def get_success_message(status_code):
    success_messages = {
        200: "Request successful.",
        201: "Resource created successfully.",
        204: "No content.",
        206: "Partial content.",
        301: "Resource moved permanently.",
        302: "Resource found.",
        304: "Resource not modified.",
        307: "Temporary redirect.",
        308: "Permanent redirect."
    }
    return success_messages.get(status_code, "Success.")
 
def get_client_error_message(status_code):
    client_error_messages = {
        400: "Bad request. Please check your request syntax.",
        401: "Unauthorized. Please authenticate.",
        403: "Forbidden. You are not allowed to access this resource.",
        404: "Resource not found.",
        405: "Method not allowed for this resource.",
        408: "Request timeout.",
        409: "Conflict. The request could not be completed due to a conflict with the current state of the resource.",
        410: "Gone. The requested resource is no longer available.",
        413: "Payload too large. The request entity is larger than the server is willing or able to process.",
        414: "URI too long. The URI provided was too long for the server to process.",
        415: "Unsupported media type. The server does not support the media type transmitted in the request.",
        429: "Too many requests. The user has sent too many requests in a given amount of time."
    }
    return client_error_messages.get(status_code, "Client error.")
 
def get_server_error_message(status_code):
    server_error_messages = {
        500: "Internal server error. Please try again later.",
        501: "Not implemented. The server does not support the functionality required to fulfill the request.",
        502: "Bad gateway. The server received an invalid response from the upstream server while processing the request.",
        503: "Service unavailable. The server is currently unable to handle the request due to temporary overload or maintenance of the server.",
        504: "Gateway timeout. The server did not receive a timely response from the upstream server while trying to fulfill the request.",
        505: "HTTP version not supported. The server does not support the HTTP protocol version used in the request."
    }
    return server_error_messages.get(status_code, "Server error.")
