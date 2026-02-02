from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Event
import re
from datetime import datetime

events_bp = Blueprint("events", __name__)

def validate_date(date_string):
    """Validate date format (YYYY-MM-DD)"""
    if not date_string:
        return False
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_positive_number(value):
    """Validate positive numeric values"""
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False

@events_bp.route("/", methods=["POST"])
@login_required
def add_event():
    if current_user.role not in ['admin', 'finance']:
        return jsonify({"error": "Unauthorized. Admin or finance role required."}), 403
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    # Validate required fields
    if not data.get("name") or not data.get("name").strip():
        return jsonify({"error": "Event name is required"}), 400
    
    if not data.get("date") or not validate_date(data["date"]):
        return jsonify({"error": "Valid date (YYYY-MM-DD) is required"}), 400
    
    if "budget" not in data or not validate_positive_number(data["budget"]):
        return jsonify({"error": "Budget must be a positive number"}), 400
    
    try:
        event = Event(
            name=data["name"].strip(),
            date=datetime.strptime(data["date"], '%Y-%m-%d').date(),
            budget=float(data["budget"]),
            footfall=int(data.get("footfall", 0)),
            revenue=float(data.get("revenue", 0.00))
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            "message": "Event added successfully",
            "event": {
                "id": event.id,
                "name": event.name,
                "date": event.date.isoformat(),
                "budget": float(event.budget),
                "footfall": event.footfall,
                "revenue": float(event.revenue)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create event: {str(e)}"}), 500

@events_bp.route("/", methods=["GET"])
@login_required
def get_events():
    try:
        events = Event.query.order_by(Event.date.desc()).all()
        
        result = []
        for e in events:
            result.append({
                "id": e.id,
                "name": e.name,
                "date": e.date.isoformat(),
                "budget": float(e.budget),
                "footfall": e.footfall,
                "revenue": float(e.revenue)
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch events: {str(e)}"}), 500

@events_bp.route("/<int:event_id>", methods=["GET"])
@login_required
def get_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        
        return jsonify({
            "id": event.id,
            "name": event.name,
            "date": event.date.isoformat(),
            "budget": float(event.budget),
            "footfall": event.footfall,
            "revenue": float(event.revenue),
            "created_at": event.created_at.isoformat() if event.created_at else None
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch event: {str(e)}"}), 500

@events_bp.route("/<int:event_id>", methods=["PUT"])
@login_required
def update_event(event_id):
    if current_user.role not in ['admin', 'finance']:
        return jsonify({"error": "Unauthorized. Admin or finance role required."}), 403
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    try:
        event = Event.query.get_or_404(event_id)
        
        # Validate date if provided
        if "date" in data:
            if not validate_date(data["date"]):
                return jsonify({"error": "Valid date (YYYY-MM-DD) is required"}), 400
            event.date = datetime.strptime(data["date"], '%Y-%m-%d').date()
        
        # Validate numeric fields if provided
        if "budget" in data:
            if not validate_positive_number(data["budget"]):
                return jsonify({"error": "Budget must be a positive number"}), 400
            event.budget = float(data["budget"])
        
        if "footfall" in data:
            if not isinstance(data["footfall"], int) or data["footfall"] < 0:
                return jsonify({"error": "Footfall must be a non-negative integer"}), 400
            event.footfall = data["footfall"]
        
        if "revenue" in data:
            if not validate_positive_number(data["revenue"]):
                return jsonify({"error": "Revenue must be a positive number"}), 400
            event.revenue = float(data["revenue"])
        
        # Update name if provided
        if "name" in data:
            if not data["name"] or not data["name"].strip():
                return jsonify({"error": "Event name is required"}), 400
            event.name = data["name"].strip()
        
        db.session.commit()
        
        return jsonify({
            "message": "Event updated successfully",
            "event": {
                "id": event.id,
                "name": event.name,
                "date": event.date.isoformat(),
                "budget": float(event.budget),
                "footfall": event.footfall,
                "revenue": float(event.revenue)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update event: {str(e)}"}), 500

@events_bp.route("/<int:event_id>", methods=["DELETE"])
@login_required
def delete_event(event_id):
    if current_user.role not in ['admin', 'finance']:
        return jsonify({"error": "Unauthorized. Admin or finance role required."}), 403
    
    try:
        event = Event.query.get_or_404(event_id)
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({"message": "Event deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete event: {str(e)}"}), 500