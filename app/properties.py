from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Property
from . import db
from .utils import login_required

properties_bp = Blueprint('properties', __name__)

@properties_bp.route('/', methods=['GET'])
@login_required
def list_properties():
    user_id = session['user_id']
    properties = Property.query.filter_by(user_id=user_id).all()
    return render_template('properties.html', properties=properties)

@properties_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_property():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        ptype = request.form.get('type', '').strip()
        location = request.form.get('location', '').strip()
        base_price = request.form.get('base_price', '0').strip()
        
        if not name:
            flash('Property name is required.', 'danger')
            return render_template('property_form.html', property=None)
            
        property = Property(
            user_id=session['user_id'],
            name=name,
            type=ptype,
            location=location,
            base_price=base_price
        )
        
        db.session.add(property)
        db.session.commit()
        
        flash('Property created successfully!', 'success')
        return redirect(url_for('properties.list_properties'))
        
    return render_template('property_form.html', property=None)

@properties_bp.route('/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property = Property.query.filter_by(id=property_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        property.name = request.form.get('name', '').strip()
        property.type = request.form.get('type', '').strip()
        property.location = request.form.get('location', '').strip()
        property.base_price = request.form.get('base_price', '0').strip()
        
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('properties.list_properties'))
        
    return render_template('property_form.html', property=property)

@properties_bp.route('/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    property = Property.query.filter_by(id=property_id, user_id=session['user_id']).first_or_404()
    
    db.session.delete(property)
    db.session.commit()
    
    flash('Property deleted successfully.', 'info')
    return redirect(url_for('properties.list_properties'))