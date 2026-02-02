from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Sponsor
import re

sponsors_bp = Blueprint("sponsors", __name__)

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Simple phone validation"""
    if not phone:
        return True  # Phone is optional
    # Remove spaces, dashes, parentheses
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return clean_phone.isdigit() and len(clean_phone) >= 10

@sponsors_bp.route("/", methods=["POST"])
@login_required
def add_sponsor():
    if current_user.role not in ['admin', 'finance']:
        return jsonify({"error": "Unauthorized. Admin or finance role required."}), 403
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    # Validate required fields
    if not data.get("name") or not data.get("name").strip():
        return jsonify({"error": "Sponsor name is required"}), 400
    
    # Validate optional fields
    email = data.get("email")
    if email and not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    phone = data.get("phone")
    if phone and not validate_phone(phone):
        return jsonify({"error": "Invalid phone number format"}), 400
    
    try:
        sponsor = Sponsor(
            name=data["name"].strip(),
            industry=data.get("industry", "").strip() or None,
            contact_person=data.get("contact_person", "").strip() or None,
            email=data.get("email", "").strip() or None,
            phone=data.get("phone", "").strip() or None,
            total_invested=0.00
        )
        
        db.session.add(sponsor)
        db.session.commit()
        
        return jsonify({
            "message": "Sponsor added successfully",
            "sponsor": {
                "id": sponsor.id,
                "name": sponsor.name,
                "industry": sponsor.industry,
                "contact_person": sponsor.contact_person,
                "email": sponsor.email,
                "phone": sponsor.phone,
                "total_invested": float(sponsor.total_invested)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create sponsor: {str(e)}"}), 500

@sponsors_bp.route("/", methods=["GET"])
@login_required
def get_sponsors():
    try:
        sponsors = Sponsor.query.all()
        
        result = []
        for s in sponsors:
            result.append({
                "id": s.id,
                "name": s.name,
                "industry": s.industry,
                "contact_person": s.contact_person,
                "email": s.email,
                "phone": s.phone,
                "total_invested": float(s.total_invested) if s.total_invested else 0.00
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sponsors: {str(e)}"}), 500

@sponsors_bp.route("/<int:sponsor_id>", methods=["GET"])
@login_required
def get_sponsor(sponsor_id):
    try:
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        
        return jsonify({
            "id": sponsor.id,
            "name": sponsor.name,
            "industry": sponsor.industry,
            "contact_person": sponsor.contact_person,
            "email": sponsor.email,
            "phone": sponsor.phone,
            "total_invested": float(sponsor.total_invested) if sponsor.total_invested else 0.00,
            "created_at": sponsor.created_at.isoformat() if sponsor.created_at else None
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sponsor: {str(e)}"}), 500

@sponsors_bp.route("/<int:sponsor_id>", methods=["PUT"])
@login_required
def update_sponsor(sponsor_id):
    if current_user.role not in ['admin', 'finance']:
        return jsonify({"error": "Unauthorized. Admin or finance role required."}), 403
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    try:
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        
        # Validate email if provided
        email = data.get("email")
        if email and not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate phone if provided
        phone = data.get("phone")
        if phone and not validate_phone(phone):
            return jsonify({"error": "Invalid phone number format"}), 400
        
        # Update fields
        if "name" in data:
            if not data["name"] or not data["name"].strip():
                return jsonify({"error": "Sponsor name is required"}), 400
            sponsor.name = data["name"].strip()
        
        sponsor.industry = data.get("industry", "").strip() or None
        sponsor.contact_person = data.get("contact_person", "").strip() or None
        sponsor.email = data.get("email", "").strip() or None
        sponsor.phone = data.get("phone", "").strip() or None
        
        db.session.commit()
        
        return jsonify({
            "message": "Sponsor updated successfully",
            "sponsor": {
                "id": sponsor.id,
                "name": sponsor.name,
                "industry": sponsor.industry,
                "contact_person": sponsor.contact_person,
                "email": sponsor.email,
                "phone": sponsor.phone,
                "total_invested": float(sponsor.total_invested) if sponsor.total_invested else 0.00
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update sponsor: {str(e)}"}), 500

@sponsors_bp.route("/<int:sponsor_id>", methods=["DELETE"])
@login_required
def delete_sponsor(sponsor_id):
    if current_user.role not in ['admin', 'finance']:
        return jsonify({"error": "Unauthorized. Admin or finance role required."}), 403
    
    try:
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        
        db.session.delete(sponsor)
        db.session.commit()
        
        return jsonify({"message": "Sponsor deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete sponsor: {str(e)}"}), 500