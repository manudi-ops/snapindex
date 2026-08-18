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

class AcademicResource(db.Model):
    __tablename__ = "academic_resources"
    resourceID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey("users.userID"), nullable=False)
    categoryID = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    fileName = db.Column(db.String(255), nullable=False)
    filePath = db.Column(db.String(500), nullable=False)
    fileType = db.Column(db.String(50), nullable=False)
    uploadDate = db.Column(db.DateTime, default=datetime.utcnow)
    lastAccessDate = db.Column(db.DateTime, nullable=True)
    accessCount = db.Column(db.Integer, default=0)
    extractedText = db.Column(db.Text, nullable=True)
    ocrConfidence = db.Column(db.Float, nullable=True)
    needsReview = db.Column(db.Boolean, default=False)
    embeddingVectorID = db.Column(db.Integer, nullable=True)

class Category(db.Model):
    __tablename__ = "categories"
    categoryID = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)