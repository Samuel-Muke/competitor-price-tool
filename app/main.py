from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    """Professional landing page for Nairobi hospitality providers"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.view_dashboard'))
    return render_template('landing.html')

@main_bp.route('/features')
def features():
    return render_template('features.html')

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')