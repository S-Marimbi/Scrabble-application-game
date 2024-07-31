from flask import Blueprint, jsonify, request
from models import Member
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token


bcrypt = Bcrypt()

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': "Required field missing"}), 400

    user = Member.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': "User not found"}), 400

    pass_ok = bcrypt.check_password_hash(user.password.encode('utf-8'),password)

    if not pass_ok:
        return jsonify({'message': "Invalid password"}), 401    

    access_token = create_access_token(
        identity = {"member_id": user.id, "user_name":user.user_name}
    )


   
    return jsonify({'user': {'user_name': user.user_name, 'email': user.email}, 'token': access_token})
