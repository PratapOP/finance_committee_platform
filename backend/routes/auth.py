"""
Enhanced Authentication Routes with Input Validation and Error Handling
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import FCMember
import re
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password validation - at least 8 chars, one uppercase, one lowercase, one number"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration with validation"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        required_fields = ["name", "email", "password"]
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({"error": f"{field.capitalize()} is required"}), 400
        
        name = str(data["name"]).strip()
        email = str(data["email"]).strip().lower()
        password = str(data["password"])
        
        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Validate name length
        if len(name) < 2 or len(name) > 120:
            return jsonify({"error": "Name must be between 2 and 120 characters"}), 400
        
        # Check if user already exists
        if FCMember.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400
        
        # Create new user
        user = FCMember(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=data.get("role", "finance")  # Default to finance role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "Registration successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """User login with validation"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Find user
        user = FCMember.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check password
        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Login user
        login_user(user, remember=data.get("remember", False))
        
        # Update last login time (optional - would need last_login column in model)
        # user.last_login = datetime.utcnow()
        # db.session.commit()
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            },
            "token": "mock-jwt-token"  # In production, generate real JWT
        })
        
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """User logout"""
    try:
        logout_user()
        return jsonify({"message": "Logout successful"})
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

@auth_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        return jsonify({
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get profile: {str(e)}"}), 500

@auth_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """Update current user profile"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        user = current_user
        
        # Update name if provided
        if "name" in data:
            name = str(data["name"]).strip()
            if len(name) < 2 or len(name) > 120:
                return jsonify({"error": "Name must be between 2 and 120 characters"}), 400
            user.name = name
        
        # Update email if provided and different
        if "email" in data and data["email"] != user.email:
            email = str(data["email"]).strip().lower()
            if not validate_email(email):
                return jsonify({"error": "Invalid email format"}), 400
            
            # Check if email is already taken
            if FCMember.query.filter(FCMember.email == email, FCMember.id != user.id).first():
                return jsonify({"error": "Email already registered by another user"}), 400
            
            user.email = email
        
        # Update password if provided
        if "current_password" in data and "new_password" in data:
            if not check_password_hash(user.password_hash, data["current_password"]):
                return jsonify({"error": "Current password is incorrect"}), 401
            
            is_valid, message = validate_password(data["new_password"])
            if not is_valid:
                return jsonify({"error": message}), 400
            
            user.password_hash = generate_password_hash(data["new_password"])
        
        db.session.commit()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Profile update failed: {str(e)}"}), 500

@auth_bp.route("/check-auth", methods=["GET"])
@login_required
def check_auth():
    """Check if user is authenticated"""
    try:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role
            }
        })
    except Exception as e:
        return jsonify({"error": f"Auth check failed: {str(e)}"}), 500

@auth_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    """Get all users (admin only)"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        users = FCMember.query.all()
        return jsonify({
            "users": [{
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active
            } for user in users]
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get users: {str(e)}"}), 500

@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Prevent self-deletion
        if user_id == current_user.id:
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        user = FCMember.query.get_or_404(user_id)
        
        # Prevent deleting the last admin
        if user.role == 'admin':
            admin_count = FCMember.query.filter_by(role='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot delete the last admin account"}), 400
        
        # Soft delete by deactivating
        user.is_active = False
        db.session.commit()
        
        return jsonify({"message": "User deactivated successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

@auth_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@login_required
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.json
        if not data or "role" not in data:
            return jsonify({"error": "Role is required"}), 400
        
        new_role = data["role"]
        if new_role not in ['admin', 'finance']:
            return jsonify({"error": "Invalid role. Must be 'admin' or 'finance'"}), 400
        
        user = FCMember.query.get_or_404(user_id)
        
        # Prevent removing admin role from last admin
        if user.role == 'admin' and new_role != 'admin':
            admin_count = FCMember.query.filter_by(role='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot remove admin role from last admin"}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            "message": "User role updated successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user role: {str(e)}"}), 500

@auth_bp.route("/users/<int:user_id>/toggle-status", methods=["PUT"])
@login_required
def toggle_user_status(user_id):
    """Activate/deactivate user (admin only)"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Prevent self-deactivation
        if user_id == current_user.id:
            return jsonify({"error": "Cannot deactivate your own account"}), 400
        
        user = FCMember.query.get_or_404(user_id)
        
        # Prevent deactivating last admin
        if user.role == 'admin' and user.is_active:
            admin_count = FCMember.query.filter_by(role='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Cannot deactivate the last admin account"}), 400
        
        user.is_active = not user.is_active
        status_text = "activated" if user.is_active else "deactivated"
        
        db.session.commit()
        
        return jsonify({
            "message": f"User {status_text} successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to toggle user status: {str(e)}"}), 500