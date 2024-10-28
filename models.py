# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class QuestionBank(db.Model):
    __tablename__ = 'question_bank'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(255), nullable=False)  # Assuming options are stored as strings

class Option(db.Model):
    __tablename__ = 'options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.id'), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)
