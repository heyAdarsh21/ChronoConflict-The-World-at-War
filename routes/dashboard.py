"""
Dashboard routes
"""

from flask import Blueprint, render_template, jsonify, session
from models import Resource, Territory, IntelligenceReport, Battle
from datetime import datetime
import json

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
def index():
    """Main dashboard view"""
    return render_template('dashboard/index.html')

@bp.route('/api/resources')
def get_resources():
    """Get resource data for visualization"""
    # Get latest resource data for major powers
    nations = ['Germany', 'USA', 'USSR', 'United Kingdom', 'Japan']
    resources_data = {}
    
    for nation in nations:
        latest = Resource.query.filter_by(nation=nation).order_by(Resource.date.desc()).first()
        if latest:
            resources_data[nation] = {
                'oil': latest.oil or 0,
                'steel': latest.steel or 0,
                'manpower': latest.manpower or 0,
                'gdp': latest.gdp or 0,
                'morale': latest.morale or 0,
                'territory_count': latest.territory_count or 0
            }
    
    return jsonify(resources_data)

@bp.route('/api/territories')
def get_territories():
    """Get territory control data"""
    territories = Territory.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'lat': t.latitude,
        'lng': t.longitude,
        'controlled_by': t.controlled_by,
        'strategic_value': t.strategic_value,
        'region': t.region
    } for t in territories])

@bp.route('/api/intelligence')
def get_intelligence():
    """Get recent intelligence reports"""
    reports = IntelligenceReport.query.order_by(IntelligenceReport.date.desc()).limit(10).all()
    return jsonify([{
        'id': r.id,
        'date': r.date.isoformat(),
        'classification': r.classification,
        'source': r.source,
        'content': r.content,
        'decoded': r.decoded,
        'side': r.side,
        'location': r.location
    } for r in reports])

@bp.route('/api/battles')
def get_battles():
    """Get battle data for map markers"""
    battles = Battle.query.all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'start_date': b.start_date.isoformat(),
        'end_date': b.end_date.isoformat() if b.end_date else None,
        'location': b.location,
        'lat': b.latitude,
        'lng': b.longitude,
        'victor': b.victor,
        'axis_casualties': b.axis_casualties,
        'allied_casualties': b.allied_casualties
    } for b in battles])

