"""
API routes for data endpoints
"""

from flask import Blueprint, jsonify, request
from models import Battle, Operation, Resource, Territory, IntelligenceReport
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/stats')
def get_stats():
    """Get overall statistics"""
    total_battles = Battle.query.count()
    total_operations = Operation.query.count()
    total_territories = Territory.query.count()
    
    return jsonify({
        'total_battles': total_battles,
        'total_operations': total_operations,
        'total_territories': total_territories,
        'date_range': {
            'start': '1939-09-01',
            'end': '1945-09-02'
        }
    })

