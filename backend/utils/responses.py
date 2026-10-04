from flask import jsonify

def success_response(data=None, status_code=200):
    return jsonify(data), status_code

def error_response(message, status_code=400, errors=None):
    payload = {
        'status': status_code,
        'message': message
    }
    if errors is not None:
        payload['errors'] = errors
    return jsonify(payload), status_code
