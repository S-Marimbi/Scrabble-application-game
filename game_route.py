from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity
from models import db, Game
import json
from util import to_int
import random

game_blueprint = Blueprint('game', __name__)

@game_blueprint.route('/game/board', methods=['GET'])
@jwt_required()
def get_board():
    current_user = get_jwt_identity()
    print(current_user)
    game = Game.query.filter_by(member_id=current_user['member_id']).first()
    print(game)
    if not game:
       return jsonify({'message': 'Game does not exist'}), 404
    board = json.loads(game.board)
    return jsonify({'message': f"Hi, {current_user['user_name']} this is your board", 'board':board})


@game_blueprint.route("/game/rack", methods=["PUT"])
@jwt_required()
def get_rack():
    current_user = get_jwt_identity()
    print(current_user)
    game = Game.query.filter_by(member_id=current_user['member_id']).first()
    if not game:
       return jsonify({'message': 'Game does not exist'}), 404

    letter_no = {
        'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12,
        'F': 2, 'G': 3, 'H': 2, 'I': 9, 'J': 1,
        'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8,
        'P': 2, 'Q': 1, 'R': 6, 'S': 4, 'T': 6,
        'U': 4, 'V': 2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1
    }
    letter_bag = []

    for letter, count in letter_no.items():
        letter_bag.extend([letter] * count)
    random.shuffle(letter_bag)
    player_rack = []
    for _ in range(7):
        tile = letter_bag.pop()
        player_rack.append(tile)

    game.rack = json.dumps(player_rack)
    db.session.commit()
    return jsonify({'message': f"{current_user['user_name']} rack", 'rack': player_rack})