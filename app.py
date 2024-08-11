from flask import Flask,request,jsonify
from models import db, Member, Game
from config import Config
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token,jwt_required, get_jwt_identity
from game_engine import create_board
import json
from flask_cors import CORS

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from game_route import game_blueprint
    app.register_blueprint(game_blueprint)

    return app

    



app = create_app()
CORS(app)
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

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = Member.query.filter_by(email=email).first()

    if not email or not password:
        return jsonify({'message': "Required field missing"}), 400
    if not user:
        return jsonify({'message': "User not found"}), 400

    pass_ok = bcrypt.check_password_hash(user.password.encode('utf-8'),password)

    if not pass_ok:
        return jsonify({'message': "Invalid password"}), 401    
   
    access_token = create_access_token(
        identity = {"id": user.id, "user_name":user.user_name}
    )
    
    if not user.game:
        member_id = user.id
        board = json.dumps(create_board())
        print(board)
        game = Game(        
            member_id=member_id, 
            board=board,
            player_rack=json.dumps([]),
            computer_rack=json.dumps([])
        )    

        db.session.add(game)
        db.session.commit()

    return jsonify({'user': {'user_name': user.user_name, 'email': user.email}, 'token': access_token})

    

    


if __name__ == '__main__':
    app.run(debug=True, port=9000)
