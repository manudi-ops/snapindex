from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from db.models import db, User

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    full_name = data.get("fullName")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(fullName=full_name, email=email, passwordHash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful", "userID": new_user.userID}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.passwordHash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful", "userID": user.userID, "fullName": user.fullName}), 200