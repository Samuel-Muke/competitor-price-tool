from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    properties = db.relationship('Property', backref='user', cascade="all, delete-orphan")

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))
    location = db.Column(db.String(255))
    base_price = db.Column(db.Numeric(10,2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CompetitorPrice(db.Model):
    __tablename__ = 'competitor_prices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)
    competitor_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    availability = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    predicted_price = db.Column(db.Numeric(10,2), nullable=False)
    model_info = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)