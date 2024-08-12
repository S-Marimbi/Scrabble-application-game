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

@game_blueprint.route('/game/board', methods=["GET"])
@jwt_required()
def get_board():
    current_user = get_jwt_identity()
    
    game = Game.query.filter_by(member_id=current_user['id']).first()
    if not game:
        return jsonify({'message': 'Game does not exist'}), 404
    
    
    board = json.loads(game.board)
    
    
    player_rack = json.loads(game.player_rack) if game.player_rack else []
    computer_rack = json.loads(game.computer_rack) if game.computer_rack else []
    
    
    if len(player_rack) < 7 or len(computer_rack) < 7:
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
        
        
        while len(player_rack) < 7:
            player_rack.append(letter_bag.pop())
        
        
        while len(computer_rack) < 7:
            computer_rack.append(letter_bag.pop())
        
        
        game.player_rack = json.dumps(player_rack)
        game.computer_rack = json.dumps(computer_rack)
        db.session.commit()
    
    return jsonify({
        'message': f"Hi, {current_user['user_name']} this is your board and racks",
        'board': board,
        'player_rack': player_rack,
        'computer_rack': computer_rack
    })



@game_blueprint.route('/game/rack', methods=["GET"])
@jwt_required()
def generate_rack():
    current_user = get_jwt_identity()
    
    game = Game.query.filter_by(member_id=current_user['id']).first()
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
    
    
    player_rack = [letter_bag.pop() for _ in range(7)]
    
    
    computer_rack = [letter_bag.pop() for _ in range(7)]
    
    
    game.player_rack = json.dumps(player_rack)
    game.computer_rack = json.dumps(computer_rack)
    db.session.commit()
    
    return jsonify({
        'message': f"{current_user['user_name']}, here is your new rack",
        'player_rack': player_rack,
        'computer_rack': computer_rack
    })

@game_blueprint.route('/game/move', methods=["POST"])
@jwt_required()
def human_move():
    current_user = get_jwt_identity()
    
    game = Game.query.filter_by(member_id=current_user['id']).first()
    if not game:
        return jsonify({'message': 'Game does not exist'}), 404

    board = json.loads(game.board)
    player_rack = json.loads(game.player_rack)

    data = request.get_json()
    word = data.get('word').upper()
    row = int(data.get('row'))
    col = int(data.get('col'))
    direction = data.get('direction').upper()

    def can_form_word(word, rack):
        rack_counter = Counter(rack)
        word_counter = Counter(word)
        for letter, count in word_counter.items():
            if rack_counter[letter] < count:
                return False
        return True

    if not can_form_word(word, player_rack):
        return jsonify({'message': "You don't have the letters to play this word."}), 400

    valid_move = True
    played_letters = []

    if direction == 'H':
        if col + len(word) > 15:
            valid_move = False
        else:
            for i, letter in enumerate(word):
                board[row][col + i] = letter
                player_rack.remove(letter)
                played_letters.append(letter)
    elif direction == 'V':
        if row + len(word) > 15:
            valid_move = False
        else:
            for i, letter in enumerate(word):
                board[row + i][col] = letter
                player_rack.remove(letter)
                played_letters.append(letter)
    else:
        valid_move = False

    if not valid_move:
        return jsonify({'message': 'Invalid move. The word does not fit on the board.'}), 400

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

    for _ in range(len(played_letters)):
        if letter_bag:
            player_rack.append(letter_bag.pop())

    game.board = json.dumps(board)
    game.player_rack = json.dumps(player_rack)
    db.session.commit()

    return jsonify({
        'message': f"Word '{word}' placed successfully on the board.",
        'board': board,
        'player_rack': player_rack
    })

@game_blueprint.route('/game/swap', methods=["POST"])
@jwt_required()
def swap_rack():
    current_user = get_jwt_identity()
    
    game = Game.query.filter_by(member_id=current_user['id']).first()
    if not game:
        return jsonify({'message': 'Game does not exist'}), 404

    player_rack = json.loads(game.player_rack)

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

    if len(letter_bag) >= len(player_rack):
        new_rack = [letter_bag.pop() for _ in range(len(player_rack))]
        player_rack = new_rack
    else:
        return jsonify({'message': 'Not enough tiles left to swap.'}), 400

    game.player_rack = json.dumps(player_rack)
    db.session.commit()

    return jsonify({
        'message': f"{current_user['user_name']}, here is your new rack",
        'player_rack': player_rack
    })


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

        while attempts < 1000000:
            row, col, direction = random.randint(0, 14), random.randint(0, 14), random.choice(['H', 'V'])
            attempts += 1

            
            if (direction == 'H' and col + len(word) <= 15) or (direction == 'V' and row + len(word) <= 15):
                for i, letter in enumerate(word):
                    if direction == 'H':
                        current_board[row][col + i] = letter
                    else:
                        current_board[row + i][col] = letter
                    rack.remove(letter)

                
                game.board = json.dumps(current_board)
                game.computer_rack = json.dumps(rack)
                db.session.commit()

            return jsonify(
                    {
                        'message': "Computer played",
                        'word': word, 
                    }
                ), 200

        return jsonify({'message': 'Failed to place word on board.'}), 400

    return play_word(computer_rack, current_board)

@game_blueprint.route('/game/skip', methods=["POST"])
@jwt_required()
def skip_turn():
    current_user = get_jwt_identity()
    game = Game.query.filter_by(member_id=current_user['id']).first()

    if game: 
        return computer_move()
        
    else: 
        return jsonify({'message': 'Game does not exist'}), 404
   
@game_blueprint.route('/game/newgame', methods=["POST"])
@jwt_required()
def new_game():
    current_user = get_jwt_identity()
    game = Game.query.filter_by(member_id=current_user['id']).first()

    if game:
        new_board = json.dumps(create_board())
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

        game.board = new_board
        game.player_rack = json.dumps(player_rack)
        game.computer_rack = json.dumps(computer_rack)

        db.session.commit()

        return jsonify({
            'message': f"Hi, {current_user['user_name']} this is your new board and racks",
            "board": json.loads(new_board),
            "player_rack": player_rack,
            "computer_rack": computer_rack
        }), 200
    else:
        return jsonify({'message': 'No existing game found.'}), 404

@game_blueprint.route("/game/logout", methods=["POST"])
@jwt_required()
def logout():
    current_user = get_jwt_identity() 
    username = current_user.get('user_name') 
    return jsonify({"message": f"{username} you have successfully logged out"}), 200
