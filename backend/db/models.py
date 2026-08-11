from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    userID = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)
    lastLogin = db.Column(db.DateTime, nullable=True)