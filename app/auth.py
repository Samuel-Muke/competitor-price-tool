import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from .models import User
from . import db

auth_bp = Blueprint('auth', __name__)

class RegistrationForm(FlaskForm):
    email = StringField('Email', [
        validators.Email(),
        validators.Length(min=6, max=255),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.Length(min=8, max=100),
        validators.DataRequired(),
        validators.Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
            message='Password must contain at least one lowercase letter, one uppercase letter, and one number'
        )
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.EqualTo('password', message='Passwords must match'),
        validators.DataRequired()
    ])

class LoginForm(FlaskForm):
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

def validate_password_strength(password):
    """Password strength validator for Nairobi market security"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Strong password"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        print(f"Form validated: {form.validate()}")
        
        if form.validate():
            email = form.email.data.strip().lower()
            password = form.password.data
            
            print(f"🔐 Login attempt for: {email}")
            print(f"🔐 Password provided: {password}")
            
            user = User.query.filter_by(email=email).first()
            print(f"👤 User found: {user is not None}")
            
            if user:
                print(f"🔑 User ID: {user.id}")
                print(f"🔑 Stored hash: {user.password_hash}")
                print(f"🔑 Hash length: {len(user.password_hash) if user.password_hash else 0}")
                
                # Test the password check step by step
                from werkzeug.security import check_password_hash
                password_match = check_password_hash(user.password_hash, password)
                print(f"🔑 Direct check_password_hash result: {password_match}")
                
                print(f"🔑 User.check_password() result: {user.check_password(password)}")
                print(f"🔒 User locked status: {user.is_locked()}")
            
            if user and user.check_password(password):
                user.reset_login_attempts()
                db.session.commit()
                
                session['user_id'] = user.id
                session['user_email'] = user.email
                flash('Karibu! Welcome to Nairobi Price Intelligence.', 'success')
                print("✅ Login successful, redirecting to dashboard")
                return redirect(url_for('dashboard.view_dashboard'))
            else:
                print("❌ Login failed - invalid credentials")
                if user:
                    user.increment_login_attempts()
                    db.session.commit()
                
                attempts_left = 5 - (user.login_attempts if user else 1)
                flash(f'Invalid email or password. {attempts_left} attempts remaining.', 'danger')  # Fixed variable name
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if request.method == 'POST':
        if form.validate():
            email = form.email.data.strip().lower()
            password = form.password.data
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered. Please login instead.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Create new user
            user = User(email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please login to continue.', 'success')
            return redirect(url_for('auth.login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return render_template('register.html', form=form)

@auth_bp.route('/validate-password', methods=['POST'])
def validate_password():
    """AJAX endpoint for real-time password validation"""
    password = request.json.get('password', '')
    is_valid, message = validate_password_strength(password)
    
    return jsonify({
        'valid': is_valid,
        'message': message,
        'strength': calculate_password_strength(password)
    })

def calculate_password_strength(password):
    """Calculate password strength score (0-100)"""
    score = 0
    
    # Length score
    if len(password) >= 8:
        score += 25
    if len(password) >= 12:
        score += 15
    
    # Character variety score
    if re.search(r'[a-z]', password):
        score += 15
    if re.search(r'[A-Z]', password):
        score += 15
    if re.search(r'\d', password):
        score += 15
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 15
    
    return min(score, 100)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.landing'))