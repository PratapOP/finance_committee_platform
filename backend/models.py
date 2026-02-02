from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# These will be initialized in app.py to avoid circular imports
def init_models(database_instance, login_manager_instance):
    global db, login_manager
    db = database_instance
    login_manager = login_manager_instance
    
    @login_manager.user_loader
    def load_user(user_id):
        return FCMember.query.get(int(user_id))


class FCMember(UserMixin, db.Model):
    __tablename__ = "fc_members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="finance")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        """Convert user to dictionary for JSON responses"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }


class Sponsor(db.Model):
    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    contact_person = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    total_invested = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert sponsor to dictionary for JSON responses"""
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'total_invested': float(self.total_invested) if self.total_invested else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date)
    budget = db.Column(db.Float)
    footfall = db.Column(db.Integer)
    revenue = db.Column(db.Float)


class Sponsorship(db.Model):
    __tablename__ = "sponsorships"

    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey("sponsors.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    amount = db.Column(db.Float)
    status = db.Column(db.String(50), default="negotiating")  # negotiating, confirmed, paid, cancelled
    roi = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sponsor = db.relationship("Sponsor", backref="sponsorships")
    event = db.relationship("Event", backref="sponsorships")

    def to_dict(self):
        """Convert sponsorship to dictionary for JSON responses"""
        return {
            'id': self.id,
            'sponsor_id': self.sponsor_id,
            'sponsor_name': self.sponsor.name if self.sponsor else None,
            'event_id': self.event_id,
            'event_name': self.event.name if self.event else None,
            'amount': float(self.amount) if self.amount else 0.0,
            'status': self.status,
            'roi': float(self.roi) if self.roi else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# This function will be defined in app.py to avoid circular imports
# @login_manager.user_loader
# def load_user(user_id):
#     return FCMember.query.get(int(user_id))
