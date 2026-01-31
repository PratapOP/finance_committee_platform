from flask import Blueprint, jsonify
from models import Event, Sponsorship

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/overview")
def overview():
    events = Event.query.all()
    sponsorships = Sponsorship.query.all()

    total_budget = sum(e.budget or 0 for e in events)
    total_revenue = sum(e.revenue or 0 for e in events)
    total_investment = sum(s.amount or 0 for s in sponsorships)

    profit = total_revenue - total_budget

    return jsonify({
        "total_events": len(events),
        "total_budget": total_budget,
        "total_revenue": total_revenue,
        "total_sponsor_investment": total_investment,
        "profit": profit
    })
