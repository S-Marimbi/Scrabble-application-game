from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Game
import json
from game_engine import create_board, letter_bag_rack
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

@game_blueprint.route('/game/board', methods=["GET", "PUT"])
@jwt_required()
def get_board_and_rack():
    current_user = get_jwt_identity()
    print(current_user)
    
    game = Game.query.filter_by(member_id=current_user['id']).first()
    print(game)
    if not game:
        return jsonify({'message': 'Game does not exist'}), 404
    
    board = json.loads(game.board)
    
    if request.method == "GET":
        player_rack = json.loads(game.player_rack) if game.player_rack else []
        computer_rack = json.loads(game.computer_rack) if game.computer_rack else []
        return jsonify({
            'message': f"Hi, {current_user['user_name']} this is your board and racks",
            'board': board,
            'player_rack': player_rack,
            'computer_rack': computer_rack
        })

    elif request.method == "PUT":
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
        
        player_rack = [letter_bag.pop() for _ in range(7)]
        computer_rack = [letter_bag.pop() for _ in range(7)]
        
        game.player_rack = json.dumps(player_rack)
        game.computer_rack = json.dumps(computer_rack)
        db.session.commit()
        
        return jsonify({
            'message': f"{current_user['user_name']} rack",
            'board': board,
            'player_rack': player_rack,
            'computer_rack': computer_rack
        })

@game_blueprint.route("/game/computer-move", methods=["POST"])
@jwt_required()
def computer_move():
    current_user = get_jwt_identity()
    user_id = current_user
    data = request.get_json()

    game = Game.query.filter_by(member_id=user_id).first()
    if not game:
        return jsonify({'message': 'Game does not exist'}), 404

    current_board = json.loads(game.board)
    computer_rack = json.loads(game.computer_rack)

    def play_word(rack, board, is_computer=True):
        valid_words = [word for word in dictionary if can_form_word(word, rack)]
        if not valid_words:
            return jsonify({'message': 'Computer has no valid words.'}), 400
        
        word = random.choice(valid_words)
        while True:
            row, col, direction = random.randint(0, 14), random.randint(0, 14), random.choice(['H', 'V'])
            if direction == 'H' and col + len(word) <= 15:
                if all(current_board[row][col + i] in [" ", word[i]] for i in range(len(word))):
                    break
            elif direction == 'V' and row + len(word) <= 15:
                if all(current_board[row + i][col] in [" ", word[i]] for i in range(len(word))):
                    break

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

        score = sum(letter_points[letter] for letter in word)
        return jsonify(
            {
                'message': f"Computer played: {word}",
                'board': current_board,
                'score': score
            }
        ), 200

    return play_word(computer_rack, current_board)
