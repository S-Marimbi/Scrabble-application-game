from flask import Flask,request,jsonify
from models import db, Member, Game
from config import Config
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

app = create_app()

migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    user_name = data.get('user_name')
    email = data.get('email')
    password = data.get('password')

    
    if not email or not password or not user_name:
        return jsonify({'message': "Required field missing"}), 400

    if len(email) < 4:
        return jsonify({'message': "Email too short"}), 400

    if len(user_name) < 4:
        return jsonify({'message': "Name too short"}), 400

    if len(password) < 4:
        return jsonify({'message': "Password too short"}), 400

    existing_member = Member.query.filter_by(email=email).first()

    if existing_member:
        return jsonify({'message': f"Email already in use {email}"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf8')  # decoded to store the password in the database

    member = Member(user_name=user_name, email=email, password=hashed_password)
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "Account created successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True, port=9000)