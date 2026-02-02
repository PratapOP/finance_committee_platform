from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app import db
from models import Event, Sponsorship, Sponsor, FCMember
from utils.auth_middleware import require_role, log_api_access
from datetime import datetime, timedelta

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/overview")
@login_required
@require_role('admin', 'finance')
@log_api_access
def overview():
    """Get overall analytics overview"""
    events = Event.query.all()
    sponsorships = Sponsorship.query.all()
    sponsors = Sponsor.query.all()
    users = FCMember.query.filter_by(is_active=True).all()

    total_budget = sum(e.budget or 0 for e in events)
    total_revenue = sum(e.revenue or 0 for e in events)
    total_investment = sum(s.amount or 0 for s in sponsorships)
    total_footfall = sum(e.footfall or 0 for e in events)

    profit = total_revenue - total_budget
    roi_percentage = ((total_revenue - total_budget) / total_budget * 100) if total_budget > 0 else 0

    return jsonify({
        "total_events": len(events),
        "total_budget": total_budget,
        "total_revenue": total_revenue,
        "total_sponsor_investment": total_investment,
        "total_sponsors": len(sponsors),
        "total_users": len(users),
        "total_footfall": total_footfall,
        "profit": profit,
        "roi_percentage": round(roi_percentage, 2)
    })


@analytics_bp.route("/trends")
@login_required
@require_role('admin', 'finance')
@log_api_access
def trends():
    """Get monthly trends data"""
    try:
        # Get monthly revenue trends for the last 12 months
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        # Query events by month
        monthly_data = db.session.query(
            extract('year', Event.date).label('year'),
            extract('month', Event.date).label('month'),
            func.sum(Event.budget).label('budget'),
            func.sum(Event.revenue).label('revenue'),
            func.sum(Event.footfall).label('footfall'),
            func.count(Event.id).label('event_count')
        ).filter(
            Event.date >= start_date,
            Event.date <= end_date
        ).group_by(
            extract('year', Event.date),
            extract('month', Event.date)
        ).order_by(
            extract('year', Event.date),
            extract('month', Event.date)
        ).all()
        
        # Format response
        trends_data = []
        for year, month, budget, revenue, footfall, event_count in monthly_data:
            month_date = datetime(year=int(year), month=int(month), day=1)
            trends_data.append({
                "month": month_date.strftime('%Y-%m'),
                "budget": float(budget) if budget else 0,
                "revenue": float(revenue) if revenue else 0,
                "footfall": int(footfall) if footfall else 0,
                "event_count": int(event_count) if event_count else 0,
                "profit": float((revenue or 0) - (budget or 0))
            })
        
        return jsonify({
            "trends": trends_data,
            "period": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch trends: {str(e)}"}), 500


@analytics_bp.route("/roi")
@login_required
@require_role('admin', 'finance')
@log_api_access
def roi():
    """Get ROI analytics data"""
    try:
        # Get sponsor ROI data
        sponsor_roi_data = db.session.query(
            Sponsor.id.label('sponsor_id'),
            Sponsor.name.label('sponsor_name'),
            Sponsor.industry.label('industry'),
            func.sum(Sponsorship.amount).label('total_investment'),
            func.avg(Sponsorship.roi).label('average_roi'),
            func.count(Sponsorship.id).label('sponsorship_count')
        ).join(
            Sponsorship, Sponsor.id == Sponsorship.sponsor_id
        ).group_by(
            Sponsor.id, Sponsor.name, Sponsor.industry
        ).order_by(
            func.sum(Sponsorship.amount).desc()
        ).limit(20).all()
        
        # Get event ROI data
        event_roi_data = db.session.query(
            Event.id.label('event_id'),
            Event.name.label('event_name'),
            Event.date.label('event_date'),
            Event.budget.label('budget'),
            Event.revenue.label('revenue'),
            func.sum(Sponsorship.amount).label('sponsorship_amount')
        ).outerjoin(
            Sponsorship, Event.id == Sponsorship.event_id
        ).group_by(
            Event.id, Event.name, Event.date, Event.budget, Event.revenue
        ).order_by(
            Event.date.desc()
        ).limit(20).all()
        
        # Format sponsor ROI data
        sponsors_roi = []
        for sponsor_id, sponsor_name, industry, total_investment, avg_roi, count in sponsor_roi_data:
            sponsors_roi.append({
                "sponsor_id": sponsor_id,
                "sponsor_name": sponsor_name,
                "industry": industry,
                "total_investment": float(total_investment) if total_investment else 0,
                "average_roi": float(avg_roi) if avg_roi else 0,
                "sponsorship_count": int(count) if count else 0
            })
        
        # Format event ROI data
        events_roi = []
        for event_id, event_name, event_date, budget, revenue, sponsorship_amount in event_roi_data:
            event_roi = ((float(revenue or 0) - float(budget or 0)) / float(budget or 1)) * 100
            events_roi.append({
                "event_id": event_id,
                "event_name": event_name,
                "event_date": event_date.strftime('%Y-%m-%d') if event_date else None,
                "budget": float(budget) if budget else 0,
                "revenue": float(revenue) if revenue else 0,
                "sponsorship_amount": float(sponsorship_amount) if sponsorship_amount else 0,
                "roi_percentage": round(event_roi, 2)
            })
        
        return jsonify({
            "sponsors_roi": sponsors_roi,
            "events_roi": events_roi,
            "summary": {
                "total_sponsors_analyzed": len(sponsors_roi),
                "total_events_analyzed": len(events_roi)
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch ROI data: {str(e)}"}), 500


@analytics_bp.route("/reports")
@login_required
@require_role('admin', 'finance')
@log_api_access
def reports():
    """Get various analytical reports"""
    try:
        # Get current date ranges
        today = datetime.utcnow()
        last_month = today - timedelta(days=30)
        last_quarter = today - timedelta(days=90)
        last_year = today - timedelta(days=365)
        
        # Performance metrics
        performance = {}
        
        # Event performance
        performance['events'] = {
            "total": Event.query.count(),
            "last_month": Event.query.filter(Event.date >= last_month).count(),
            "last_quarter": Event.query.filter(Event.date >= last_quarter).count(),
            "last_year": Event.query.filter(Event.date >= last_year).count()
        }
        
        # Sponsor performance
        performance['sponsors'] = {
            "total": Sponsor.query.count(),
            "active": Sponsor.query.join(Sponsorship).distinct().count()
        }
        
        # Financial performance
        events_last_month = Event.query.filter(Event.date >= last_month).all()
        performance['financial'] = {
            "last_month_revenue": sum(e.revenue or 0 for e in events_last_month),
            "last_month_budget": sum(e.budget or 0 for e in events_last_month),
            "last_month_profit": sum((e.revenue or 0) - (e.budget or 0) for e in events_last_month)
        }
        
        # Top performing sponsors
        top_sponsors = db.session.query(
            Sponsor.name,
            func.sum(Sponsorship.amount).label('total_amount')
        ).join(
            Sponsorship, Sponsor.id == Sponsorship.sponsor_id
        ).group_by(
            Sponsor.id, Sponsor.name
        ).order_by(
            func.sum(Sponsorship.amount).desc()
        ).limit(10).all()
        
        # Top performing events
        top_events = db.session.query(
            Event.name,
            Event.date,
            Event.revenue,
            Event.budget
        ).filter(
            Event.revenue.isnot(None)
        ).order_by(
            Event.revenue.desc()
        ).limit(10).all()
        
        # Industry breakdown
        industry_breakdown = db.session.query(
            Sponsor.industry,
            func.count(Sponsor.id).label('count'),
            func.sum(Sponsorship.amount).label('total_investment')
        ).join(
            Sponsorship, Sponsor.id == Sponsorship.sponsor_id
        ).group_by(
            Sponsor.industry
        ).order_by(
            func.count(Sponsor.id).desc()
        ).all()
        
        return jsonify({
            "performance": performance,
            "top_sponsors": [
                {
                    "name": name,
                    "total_amount": float(amount) if amount else 0
                } for name, amount in top_sponsors
            ],
            "top_events": [
                {
                    "name": name,
                    "date": date.strftime('%Y-%m-%d') if date else None,
                    "revenue": float(revenue) if revenue else 0,
                    "budget": float(budget) if budget else 0,
                    "profit": float((revenue or 0) - (budget or 0))
                } for name, date, revenue, budget in top_events
            ],
            "industry_breakdown": [
                {
                    "industry": industry or "Unknown",
                    "sponsor_count": int(count) if count else 0,
                    "total_investment": float(investment) if investment else 0
                } for industry, count, investment in industry_breakdown
            ],
            "generated_at": today.isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate reports: {str(e)}"}), 500


@analytics_bp.route("/dashboard")
@login_required
@require_role('admin', 'finance')
@log_api_access
def dashboard():
    """Get comprehensive dashboard analytics"""
    try:
        # Get basic counts
        total_events = Event.query.count()
        total_sponsors = Sponsor.query.count()
        total_sponsorships = Sponsorship.query.count()
        total_users = FCMember.query.filter_by(is_active=True).count()
        
        # Get financial totals
        events = Event.query.all()
        sponsorships = Sponsorship.query.all()
        
        total_budget = sum(e.budget or 0 for e in events)
        total_revenue = sum(e.revenue or 0 for e in events)
        total_investment = sum(s.amount or 0 for s in sponsorships)
        total_footfall = sum(e.footfall or 0 for e in events)
        
        # Calculate metrics
        total_profit = total_revenue - total_budget
        roi_percentage = ((total_revenue - total_budget) / total_budget * 100) if total_budget > 0 else 0
        avg_event_size = total_footfall / total_events if total_events > 0 else 0
        sponsorship_per_event = total_sponsorships / total_events if total_events > 0 else 0
        
        # Recent activity (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_events = Event.query.filter(Event.date >= recent_date).count()
        recent_sponsorships = Sponsorship.query.filter(Sponsorship.created_at >= recent_date).count()
        
        return jsonify({
            "overview": {
                "total_events": total_events,
                "total_sponsors": total_sponsors,
                "total_sponsorships": total_sponsorships,
                "total_users": total_users
            },
            "financial": {
                "total_budget": total_budget,
                "total_revenue": total_revenue,
                "total_investment": total_investment,
                "total_profit": total_profit,
                "total_footfall": total_footfall,
                "roi_percentage": round(roi_percentage, 2)
            },
            "metrics": {
                "avg_event_size": round(avg_event_size, 2),
                "sponsorship_per_event": round(sponsorship_per_event, 2),
                "avg_sponsorship_value": total_investment / total_sponsorships if total_sponsorships > 0 else 0
            },
            "recent_activity": {
                "recent_events": recent_events,
                "recent_sponsorships": recent_sponsorships
            },
            "generated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch dashboard analytics: {str(e)}"}), 500
