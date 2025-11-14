from datetime import timedelta  # Add this if missing
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    properties = db.relationship('Property', backref='user', cascade="all, delete-orphan", lazy='dynamic')
    competitor_prices = db.relationship('CompetitorPrice', backref='user', cascade="all, delete-orphan", lazy='dynamic')
    forecasts = db.relationship('Forecast', backref='user', cascade="all, delete-orphan", lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None

    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()

class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(
        'Serviced Apartment', 'Boutique Hotel', 'Guest House', 'Luxury Villa', 
        'Bed & Breakfast', 'Hostel', 'Lodge', 'Resort'
    ), nullable=False, default='Serviced Apartment')
    location = db.Column(db.Enum(
        'Westlands', 'CBD', 'Kilimani', 'Karen', 'Lavington', 'Kileleshwa', 
        'Parklands', 'Upper Hill', 'South B', 'South C', 'Ngong Road', 'Thika Road'
    ), nullable=False, default='Westlands')
    base_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), default='KES', nullable=False)
    bedrooms = db.Column(db.Integer, default=1)
    capacity = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    competitor_prices = db.relationship('CompetitorPrice', backref='property', cascade="all, delete-orphan", lazy='dynamic')
    forecasts = db.relationship('Forecast', backref='property', cascade="all, delete-orphan", lazy='dynamic')

    __table_args__ = (
        db.Index('idx_property_user_location', 'user_id', 'location'),
        db.Index('idx_property_type_location', 'type', 'location'),
    )

class CompetitorPrice(db.Model):
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)
    competitor_name = db.Column(db.String(255), nullable=False, index=True)
    platform = db.Column(db.Enum('Airbnb', 'Booking.com', 'Agoda', 'Expedia', 'Hotels.com', 'Direct Website'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='KES', nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    availability = db.Column(db.Enum('Available', 'Limited', 'Last Unit', 'Sold Out', 'Good Availability'), default='Available')
    min_stay = db.Column(db.Integer, default=1)
    rating = db.Column(db.Numeric(3, 2), nullable=True)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_competitor_user_date', 'user_id', 'date'),
        db.Index('idx_competitor_property_date', 'property_id', 'date'),
        db.Index('idx_competitor_platform', 'platform', 'date'),
        db.UniqueConstraint('user_id', 'property_id', 'competitor_name', 'date', name='unique_competitor_entry'),
    )

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    predicted_price = db.Column(db.Numeric(10, 2), nullable=False)
    confidence_interval = db.Column(db.Numeric(5, 2), default=0.80)
    model_info = db.Column(db.String(255))
    seasonality_factor = db.Column(db.Numeric(5, 2), default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_forecast_user_property', 'user_id', 'property_id'),
        db.Index('idx_forecast_date', 'date'),
        db.UniqueConstraint('user_id', 'property_id', 'date', name='unique_forecast_entry'),
    )