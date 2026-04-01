"""
Timeline routes
"""

from flask import Blueprint, render_template, jsonify, request
from models import Battle, Operation
from datetime import datetime

bp = Blueprint('timeline', __name__, url_prefix='/timeline')

@bp.route('/')
def index():
    """Timeline viewer"""
    return render_template('timeline/index.html')

@bp.route('/api/events')
def get_events():
    """Get timeline events"""
    start_year = request.args.get('start_year', 1939, type=int)
    end_year = request.args.get('end_year', 1945, type=int)
    
    # Get battles in date range
    battles = Battle.query.filter(
        Battle.start_date >= datetime(start_year, 1, 1),
        Battle.start_date <= datetime(end_year, 12, 31)
    ).order_by(Battle.start_date).all()
    
    # Get operations in date range
    operations = Operation.query.filter(
        Operation.start_date >= datetime(start_year, 1, 1),
        Operation.start_date <= datetime(end_year, 12, 31)
    ).order_by(Operation.start_date).all()
    
    events = []
    
    for battle in battles:
        events.append({
            'type': 'battle',
            'id': battle.id,
            'name': battle.name,
            'date': battle.start_date.isoformat(),
            'location': battle.location,
            'victor': battle.victor,
            'description': battle.description
        })
    
    for op in operations:
        events.append({
            'type': 'operation',
            'id': op.id,
            'name': op.name,
            'code_name': op.code_name,
            'date': op.start_date.isoformat(),
            'side': op.side,
            'outcome': op.outcome,
            'description': op.description
        })
    
    # Sort by date
    events.sort(key=lambda x: x['date'])
    
    return jsonify(events)

