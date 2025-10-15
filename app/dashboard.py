from datetime import date
from statistics import mean
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify, send_file
from .models import Property, CompetitorPrice, Forecast
from . import db
from .utils import login_required
import tempfile
import os
import uuid

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@login_required
def view_dashboard():
    user_id = session['user_id']
    properties = Property.query.filter_by(user_id=user_id).all()

    # Handle property selection
    selected_property = None
    selected_property_id = request.args.get('property')
    
    if properties:
        if selected_property_id:
            selected_property = next((p for p in properties if str(p.id) == str(selected_property_id)), properties[0])
        else:
            selected_property = properties[0]

    # Initialize data containers
    recent_entries = []
    metrics = {}
    chart_data = []
    forecasts = []

    if selected_property:
        # Recent competitor entries
        recent_entries = (CompetitorPrice.query
                        .filter_by(user_id=user_id, property_id=selected_property.id)
                        .order_by(CompetitorPrice.date.desc())
                        .limit(10).all())

        # Calculate metrics
        all_competitor_prices = CompetitorPrice.query.filter_by(
            user_id=user_id, property_id=selected_property.id
        ).all()
        
        metrics['competitors_tracked'] = len(set([c.competitor_name for c in all_competitor_prices]))
        metrics['total_entries'] = len(all_competitor_prices)

        # Today's price difference
        today_prices = [c.price for c in all_competitor_prices if c.date == date.today()]
        avg_today = mean(today_prices) if today_prices else None
        metrics['price_difference'] = (
            float(selected_property.base_price) - float(avg_today)
        ) if avg_today else None

        # Prepare chart data
        prices_by_date = {}
        for entry in all_competitor_prices:
            prices_by_date.setdefault(entry.date, []).append(float(entry.price))
            
        for entry_date, prices in sorted(prices_by_date.items()):
            avg_competitor = mean(prices) if prices else None
            chart_data.append({
                'date': entry_date.isoformat(),
                'base_price': float(selected_property.base_price),
                'avg_competitor': round(avg_competitor, 2) if avg_competitor is not None else None
            })

        # Get forecasts
        forecasts = (Forecast.query
                    .filter_by(user_id=user_id, property_id=selected_property.id)
                    .order_by(Forecast.date.asc()).all())

    return render_template('dashboard.html',
                    properties=properties,
                    selected_property=selected_property,
                        recent_entries=recent_entries,
                        metrics=metrics,
                        chart_data=chart_data,
                        forecasts=forecasts)

@dashboard_bp.route('/scrape/<int:property_id>')
@login_required
def run_scrape(property_id):
    from .scrape import run_scraper
    property = Property.query.filter_by(id=property_id, user_id=session['user_id']).first_or_404()
    
    entries_saved = run_scraper(
        session['user_id'], 
        property.id, 
        location=property.location, 
        limit=200, 
        headless=True
    )
    
    flash(f"Price scraping completed for {property.name}. {entries_saved} new entries saved.", "success")
    return redirect(url_for('dashboard.view_dashboard', property=property.id))

@dashboard_bp.route('/forecast/<int:property_id>')
@login_required
def run_forecast(property_id):
    from .forecast import run_forecast as generate_forecast
    property = Property.query.filter_by(id=property_id, user_id=session['user_id']).first_or_404()
    
    days_forecasted = generate_forecast(session['user_id'], property.id, horizon=7)
    flash(f'Price forecast generated for {days_forecasted} days.', 'success')
    return redirect(url_for('dashboard.view_dashboard', property=property.id))

@dashboard_bp.route('/report/csv/<int:property_id>')
@login_required
def generate_csv_report(property_id):
    try:
        from .report import make_csv
    except ImportError:
        flash('Report module not available', 'danger')
        return redirect(url_for('dashboard.view_dashboard', property=property_id))
    
    property = Property.query.filter_by(id=property_id, user_id=session['user_id']).first_or_404()
    
    # Create file in current directory with unique name
    filename = f"temp_report_{uuid.uuid4().hex}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    try:
        output_path = make_csv(session['user_id'], property_id, filepath)
        
        # Use as_attachment=False to avoid file locking issues
        response = send_file(
            output_path, 
            as_attachment=True,
            download_name=f'price_report_{property.name}_{date.today()}.csv'
        )
        
        return response
        
    except Exception as e:
        # Try to clean up on error
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass
        flash(f'CSV report generation failed: {str(e)}', 'danger')
        return redirect(url_for('dashboard.view_dashboard', property=property_id))

@dashboard_bp.route('/report/pdf/<int:property_id>')
@login_required
def generate_pdf_report(property_id):
    try:
        from .report import make_pdf
    except ImportError:
        flash('Report module not available', 'danger')
        return redirect(url_for('dashboard.view_dashboard', property=property_id))
    
    property = Property.query.filter_by(id=property_id, user_id=session['user_id']).first_or_404()
    
    # Create file in current directory with unique name
    filename = f"temp_report_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(os.getcwd(), filename)
    
    try:
        output_path = make_pdf(session['user_id'], property_id, filepath)
        
        # Use as_attachment=False to avoid file locking issues
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=f'price_report_{property.name}_{date.today()}.pdf'
        )
        
        return response
        
    except Exception as e:
        # Try to clean up on error
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass
        flash(f'PDF report generation failed: {str(e)}', 'danger')
        return redirect(url_for('dashboard.view_dashboard', property=property_id))