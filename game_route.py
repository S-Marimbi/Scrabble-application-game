from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity
from models import db, Game
import json
from game_engine import create_board,letter_bag_rack
import random
from collections import Counter


game_blueprint = Blueprint('game', __name__)

def load_dictionary(file_path):
    try:
        with open(file_path, 'r') as file:
            words = file.read().splitlines()
        return [word.upper() for word in words]
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []


dictionary_file_path = r'game_engine/dictionary.txt'
dictionary = load_dictionary(dictionary_file_path)


letter_points = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1,
    'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8,
    'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1,
    'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
    'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10
}

def can_form_word(word, rack):
    rack_counter = Counter(rack)
    word_counter = Counter(word)
    for letter, count in word_counter.items():
        if rack_counter[letter] < count:
            return False
    return True

@game_blueprint.route("/game/computer-move", methods=["POST"])
@jwt_required()
def computer_move():
    current_user = get_jwt_identity()
 

    game = Game.query.filter_by(member_id=current_user['id']).first()
    if not game:
        return jsonify({'message': 'Game does not exist'}), 404

    current_board = json.loads(game.board)
    computer_rack = json.loads(game.computer_rack)

    def play_word(rack, board, is_computer=True):
        valid_words = [word for word in dictionary if can_form_word(word, rack)]
        if not valid_words:
            return jsonify({'message': 'Computer has no valid words.'}), 400

        word = random.choice(valid_words)
        attempts = 0
        




        while attempts < 100000:
            row, col, direction = random.randint(0, 14), random.randint(0, 14), random.choice(['H', 'V'])
            
          

            attempts += 1

      
            for i, letter in enumerate(word):
                if direction == 'H':
                    current_board[row][col + i] = letter
                    computer_rack.remove(letter)
                else:
                    current_board[row + i][col] = letter
                    computer_rack.remove(letter)

            game.board = json.dumps(current_board)
            game.computer_rack = json.dumps(computer_rack)
            db.session.commit()

            
            return jsonify(
                {
                    'message': f"Computer played: {word}, row,col: {row},{col}, direction: {direction}"
                   
                }
            ), 200
 

    return play_word(computer_rack, current_board)
