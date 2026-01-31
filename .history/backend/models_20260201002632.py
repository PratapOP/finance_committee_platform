from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime


class FCMember(UserMixin, db.Model):
    __tablename__ = "fc_members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="finance")

    def get_id(self):
        return str(self.id)


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
    status = db.Column(db.String(50))  # negotiating, confirmed, paid
    roi = db.Column(db.Float)

    sponsor = db.relationship("Sponsor")
    event = db.relationship("Event")


@login_manager.user_loader
def load_user(user_id):
    return FCMember.query.get(int(user_id))
