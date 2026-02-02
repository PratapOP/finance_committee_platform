from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Sponsorship, Sponsor, Event
from utils.auth_middleware import require_role, log_api_access
import re
from datetime import datetime

sponsorships_bp = Blueprint("sponsorships", __name__)

def validate_positive_number(value):
    """Validate positive numeric values"""
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False

def validate_status(status):
    """Validate sponsorship status"""
    valid_statuses = ['negotiating', 'confirmed', 'paid', 'cancelled']
    return status in valid_statuses

@sponsorships_bp.route("/", methods=["POST"])
@login_required
@require_role('admin', 'finance')
@log_api_access
def add_sponsorship():
    """Create a new sponsorship"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        if not data.get("sponsor_id") or not data.get("event_id"):
            return jsonify({"error": "Sponsor ID and Event ID are required"}), 400
        
        if not validate_positive_number(data.get("amount", 0)):
            return jsonify({"error": "Amount must be a positive number"}), 400
        
        # Validate optional status
        status = data.get("status", "negotiating")
        if not validate_status(status):
            return jsonify({"error": "Invalid status. Must be: negotiating, confirmed, paid, or cancelled"}), 400
        
        # Check if sponsor and event exist
        sponsor = Sponsor.query.get(data["sponsor_id"])
        if not sponsor:
            return jsonify({"error": "Sponsor not found"}), 404
        
        event = Event.query.get(data["event_id"])
        if not event:
            return jsonify({"error": "Event not found"}), 404
        
        # Check for duplicate sponsorship
        existing = Sponsorship.query.filter_by(
            sponsor_id=data["sponsor_id"],
            event_id=data["event_id"]
        ).first()
        
        if existing:
            return jsonify({"error": "Sponsorship already exists for this sponsor and event"}), 400
        
        # Create sponsorship
        sponsorship = Sponsorship(
            sponsor_id=data["sponsor_id"],
            event_id=data["event_id"],
            amount=float(data["amount"]),
            status=status,
            roi=data.get("roi", 0.0)
        )
        
        db.session.add(sponsorship)
        db.session.commit()
        
        return jsonify({
            "message": "Sponsorship created successfully",
            "sponsorship": {
                "id": sponsorship.id,
                "sponsor_id": sponsorship.sponsor_id,
                "sponsor_name": sponsor.name,
                "event_id": sponsorship.event_id,
                "event_name": event.name,
                "amount": float(sponsorship.amount),
                "status": sponsorship.status,
                "roi": float(sponsorship.roi) if sponsorship.roi else 0.0
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create sponsorship: {str(e)}"}), 500

@sponsorships_bp.route("/", methods=["GET"])
@login_required
@log_api_access
def get_sponsorships():
    """Get all sponsorships with optional filtering"""
    try:
        # Query parameters
        sponsor_id = request.args.get('sponsor_id', type=int)
        event_id = request.args.get('event_id', type=int)
        status = request.args.get('status')
        
        query = Sponsorship.query
        
        # Apply filters
        if sponsor_id:
            query = query.filter(Sponsorship.sponsor_id == sponsor_id)
        if event_id:
            query = query.filter(Sponsorship.event_id == event_id)
        if status:
            if not validate_status(status):
                return jsonify({"error": "Invalid status filter"}), 400
            query = query.filter(Sponsorship.status == status)
        
        sponsorships = query.order_by(Sponsorship.created_at.desc()).all()
        
        result = []
        for sp in sponsorships:
            result.append({
                "id": sp.id,
                "sponsor_id": sp.sponsor_id,
                "sponsor_name": sp.sponsor.name if sp.sponsor else None,
                "event_id": sp.event_id,
                "event_name": sp.event.name if sp.event else None,
                "amount": float(sp.amount) if sp.amount else 0.0,
                "status": sp.status,
                "roi": float(sp.roi) if sp.roi else 0.0,
                "created_at": sp.created_at.isoformat() if hasattr(sp, 'created_at') and sp.created_at else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sponsorships: {str(e)}"}), 500

@sponsorships_bp.route("/<int:sponsorship_id>", methods=["GET"])
@login_required
@log_api_access
def get_sponsorship(sponsorship_id):
    """Get a specific sponsorship by ID"""
    try:
        sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
        
        return jsonify({
            "id": sponsorship.id,
            "sponsor_id": sponsorship.sponsor_id,
            "sponsor_name": sponsorship.sponsor.name if sponsorship.sponsor else None,
            "event_id": sponsorship.event_id,
            "event_name": sponsorship.event.name if sponsorship.event else None,
            "amount": float(sponsorship.amount) if sponsorship.amount else 0.0,
            "status": sponsorship.status,
            "roi": float(sponsorship.roi) if sponsorship.roi else 0.0,
            "created_at": sponsorship.created_at.isoformat() if hasattr(sponsorship, 'created_at') and sponsorship.created_at else None
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sponsorship: {str(e)}"}), 500

@sponsorships_bp.route("/<int:sponsorship_id>", methods=["PUT"])
@login_required
@require_role('admin', 'finance')
@log_api_access
def update_sponsorship(sponsorship_id):
    """Update a sponsorship"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
        
        # Update amount if provided
        if "amount" in data:
            if not validate_positive_number(data["amount"]):
                return jsonify({"error": "Amount must be a positive number"}), 400
            sponsorship.amount = float(data["amount"])
        
        # Update status if provided
        if "status" in data:
            if not validate_status(data["status"]):
                return jsonify({"error": "Invalid status. Must be: negotiating, confirmed, paid, or cancelled"}), 400
            sponsorship.status = data["status"]
        
        # Update ROI if provided
        if "roi" in data:
            sponsorship.roi = float(data["roi"])
        
        db.session.commit()
        
        return jsonify({
            "message": "Sponsorship updated successfully",
            "sponsorship": {
                "id": sponsorship.id,
                "sponsor_id": sponsorship.sponsor_id,
                "sponsor_name": sponsorship.sponsor.name if sponsorship.sponsor else None,
                "event_id": sponsorship.event_id,
                "event_name": sponsorship.event.name if sponsorship.event else None,
                "amount": float(sponsorship.amount) if sponsorship.amount else 0.0,
                "status": sponsorship.status,
                "roi": float(sponsorship.roi) if sponsorship.roi else 0.0
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update sponsorship: {str(e)}"}), 500

@sponsorships_bp.route("/<int:sponsorship_id>", methods=["DELETE"])
@login_required
@require_role('admin', 'finance')
@log_api_access
def delete_sponsorship(sponsorship_id):
    """Delete a sponsorship"""
    try:
        sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
        
        db.session.delete(sponsorship)
        db.session.commit()
        
        return jsonify({"message": "Sponsorship deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete sponsorship: {str(e)}"}), 500

@sponsorships_bp.route("/stats", methods=["GET"])
@login_required
@log_api_access
def get_sponsorship_stats():
    """Get sponsorship statistics"""
    try:
        total_sponsorships = Sponsorship.query.count()
        total_amount = db.session.query(db.func.sum(Sponsorship.amount)).scalar() or 0
        
        # Status breakdown
        status_stats = db.session.query(
            Sponsorship.status,
            db.func.count(Sponsorship.id),
            db.func.sum(Sponsorship.amount)
        ).group_by(Sponsorship.status).all()
        
        status_breakdown = {}
        for status, count, amount in status_stats:
            status_breakdown[status] = {
                "count": count,
                "total_amount": float(amount) if amount else 0.0
            }
        
        # Average sponsorship amount
        avg_amount = total_amount / total_sponsorships if total_sponsorships > 0 else 0
        
        return jsonify({
            "total_sponsorships": total_sponsorships,
            "total_amount": float(total_amount),
            "average_amount": float(avg_amount),
            "status_breakdown": status_breakdown
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sponsorship stats: {str(e)}"}), 500

@sponsorships_bp.route("/by-sponsor/<int:sponsor_id>", methods=["GET"])
@login_required
@log_api_access
def get_sponsorships_by_sponsor(sponsor_id):
    """Get all sponsorships for a specific sponsor"""
    try:
        # Verify sponsor exists
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        
        sponsorships = Sponsorship.query.filter_by(sponsor_id=sponsor_id)\
            .order_by(Sponsorship.created_at.desc()).all()
        
        result = []
        for sp in sponsorships:
            result.append({
                "id": sp.id,
                "sponsor_id": sp.sponsor_id,
                "sponsor_name": sponsor.name,
                "event_id": sp.event_id,
                "event_name": sp.event.name if sp.event else None,
                "event_date": sp.event.date.isoformat() if sp.event and sp.event.date else None,
                "amount": float(sp.amount) if sp.amount else 0.0,
                "status": sp.status,
                "roi": float(sp.roi) if sp.roi else 0.0,
                "created_at": sp.created_at.isoformat() if hasattr(sp, 'created_at') and sp.created_at else None
            })
        
        return jsonify({
            "sponsor": {
                "id": sponsor.id,
                "name": sponsor.name,
                "industry": sponsor.industry
            },
            "sponsorships": result,
            "total_amount": sum(sp["amount"] for sp in result),
            "sponsorship_count": len(result)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sponsor sponsorships: {str(e)}"}), 500

@sponsorships_bp.route("/by-event/<int:event_id>", methods=["GET"])
@login_required
@log_api_access
def get_sponsorships_by_event(event_id):
    """Get all sponsorships for a specific event"""
    try:
        # Verify event exists
        event = Event.query.get_or_404(event_id)
        
        sponsorships = Sponsorship.query.filter_by(event_id=event_id)\
            .order_by(Sponsorship.created_at.desc()).all()
        
        result = []
        for sp in sponsorships:
            result.append({
                "id": sp.id,
                "sponsor_id": sp.sponsor_id,
                "sponsor_name": sp.sponsor.name if sp.sponsor else None,
                "sponsor_industry": sp.sponsor.industry if sp.sponsor else None,
                "event_id": sp.event_id,
                "event_name": event.name,
                "event_date": event.date.isoformat() if event.date else None,
                "amount": float(sp.amount) if sp.amount else 0.0,
                "status": sp.status,
                "roi": float(sp.roi) if sp.roi else 0.0,
                "created_at": sp.created_at.isoformat() if hasattr(sp, 'created_at') and sp.created_at else None
            })
        
        return jsonify({
            "event": {
                "id": event.id,
                "name": event.name,
                "date": event.date.isoformat() if event.date else None,
                "budget": float(event.budget) if event.budget else 0.0
            },
            "sponsorships": result,
            "total_sponsorship": sum(sp["amount"] for sp in result),
            "sponsorship_count": len(result)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch event sponsorships: {str(e)}"}), 500