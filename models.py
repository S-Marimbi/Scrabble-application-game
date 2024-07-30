from flask_sqlalchemy import SQLalchemy, Model

db = SQLalchemy()

class Member(db.Model):
    __tablename__ = 'member'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.varchar(100), nullable=False)
    email = db.Column(db.varchar(200), nullable=False, unique=True)
    password = db.Column(db.varchar(100), nullable=False)
    game = db.relationship('Game',backref='member',uselist=False,cascade='all, delete-orphan')

    def info(self):
        return{'id':self.id, 'user_name':self.user_name, 'email':self.email}

class Game(db.Model):
    __tablename__ = 'game'
    
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.text, nullable=False)
    player_rack = db.Column(db.text, nullable=False)
    computer_rack = db.column(db.text, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete = 'CASCADE'), nullable=False, unique = True)