from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app import db
from models import FCMember

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    if FCMember.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = FCMember(
        name=data["name"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        role="admin"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "FC member registered successfully"})


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = FCMember.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)
    return jsonify({"message": "Login successful", "name": user.name})


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})
