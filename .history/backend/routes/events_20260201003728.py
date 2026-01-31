from flask import Blueprint, request, jsonify
from app import db
from models import Event

events_bp = Blueprint("events", __name__)


@events_bp.route("/", methods=["POST"])
def add_event():
    data = request.json

    event = Event(
        name=data["name"],
        date=data.get("date"),
        budget=data.get("budget"),
        footfall=data.get("footfall"),
        revenue=data.get("revenue")
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event added successfully"})


@events_bp.route("/", methods=["GET"])
def get_events():
    events = Event.query.all()

    result = []
    for e in events:
        result.append({
            "id": e.id,
            "name": e.name,
            "date": str(e.date),
            "budget": e.budget,
            "footfall": e.footfall,
            "revenue": e.revenue
        })

    return jsonify(result)
