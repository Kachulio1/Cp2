from flask import Blueprint, request, jsonify
from app.models import User
import json
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity


auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'msg':'user already exists'}), 409
    password = request.json['password']
    email = request.json['email']
    if User.query.filter_by(email=email).first():
        return jsonify({'msg':'a user with that email already exists'}), 409

    user = User(username, email, password)
    user.save()

    response = jsonify({'msg':'user created'}), 201
    return response


@auth.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    if username:
         user = User.query.filter_by(username=username).first()
         if not user:
             return jsonify({"msg": "User name does not exist!"}), 401

    password = request.json.get('password', None)
    if not user.verify_password(password):
        return jsonify({"msg": "Bad  password"}), 401
    #
    # if username != 'test' or password != 'test':
    #     return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    ret = {'access_token': create_access_token(identity=user.username)}
    return jsonify(ret), 200

@auth.route('/test', methods=['GET'])
@jwt_required
def test():
    return get_jwt_identity()