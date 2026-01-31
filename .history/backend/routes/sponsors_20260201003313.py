from flask import Blueprint, request, jsonify
from app import db
from models import Sponsor

sponsors_bp = Blueprint("sponsors", __name__)


@sponsors_bp.route("/", methods=["POST"])
def add_sponsor():
    data = request.json

    sponsor = Sponsor(
        name=data["name"],
        industry=data.get("industry"),
        contact_person=data.get("contact_person"),
        email=data.get("email"),
        phone=data.get("phone"),
        total_invested=0
    )

    db.session.add(sponsor)
    db.session.commit()

    return jsonify({"message": "Sponsor added successfully"})


@sponsors_bp.route("/", methods=["GET"])
def get_sponsors():
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
            "total_invested": s.total_invested
        })

    return jsonify(result)
