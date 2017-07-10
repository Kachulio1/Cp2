from flask import Blueprint, request, jsonify
from app.models import User
import json
from flask_jwt_extended import  create_access_token

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    if not username:
        return jsonify({'msg': 'Username is required'}), 400  # client error in the request 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'msg': 'Username has already been taken'}), 409  # 409 - Conflict
    # check if  username has invalid characters e.g. [!@#%^&]
    if not username.isalnum():
        return jsonify(
            {'msg': 'Invalid User Name Only Use Alphabet and Numbers'}), 400  # client error in the request 400

    if len(username) > 80:
        return jsonify(
            {
                'msg': 'Sorry that username is too long (should be no longer than 80 characters)'}), 400  # client error in the request 400

    password = request.json['password']

    # check if the password is empty
    if not password:
        return jsonify({'msg': "Please provide a password"}), 400  # client error in the request 400

    email = request.json['email']
    # check if the email is empty
    if not email:
        return jsonify({'msg': 'Please provide an email'}), 400  # client error in the request 400

    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'The email address you have entered is already registered'}), 409  # 409 - Conflict

    # create a user instance with the posted credentials
    user = User(username, email, password)
    # finally save the data to the database
    user.save()
    # return a successes response with a status code of 201
    response = jsonify({'msg': 'User Created'}), 201  # 201 - Created
    return response


@auth.route('/login', methods=['POST'])
def login():
    # get the user name or None if the username was not sent same for password
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    # if there was no username provided return a message and a status code also same for password
    if not username:
        return jsonify({'msg': 'Username is required'}), 400  # client error in the request
    if not password:
        return jsonify({'msg': 'Password is required'}), 400  # client error in the request

    # Query the database with the username provided
    user = User.query.filter_by(username=username).first()

    # if there was no user in the database with that name return a response
    if not user:
        return jsonify({"msg": "User name does not exist!"}), 401  # status code for authentication errors

    # check if the password is the same with the stored password
    if not user.verify_password(password):
        return jsonify({"msg": "Bad  password"}), 401  # status code for authentication errors.

    # create a token and return it with a response of 200
    ret = {'access_token': create_access_token(identity=user.username), 'msg': 'You have logged in successfully.'}

    return jsonify(ret), 200  # transmission is OK
