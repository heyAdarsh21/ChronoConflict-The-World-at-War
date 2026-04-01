"""
Aftermath and war crimes routes
"""

from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
from models import WarCrime

bp = Blueprint('aftermath', __name__, url_prefix='/aftermath')


@bp.route('/')
def index():
    """Aftermath overview"""
    return render_template('aftermath/index.html')


@bp.route('/api/events')
def list_events():
    """Return filtered list of war crimes / humanitarian events"""
    category = request.args.get('category')
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    region = request.args.get('region')

    query = WarCrime.query

    if category:
        query = query.filter(WarCrime.category == category)
    if region:
        query = query.filter(WarCrime.region.ilike(f"%{region}%"))
    if start_year:
        query = query.filter(WarCrime.event_date >= datetime(start_year, 1, 1))
    if end_year:
        query = query.filter(WarCrime.event_date <= datetime(end_year, 12, 31))

    events = query.order_by(WarCrime.event_date.asc().nullslast()).all()

    categories = [row[0] for row in WarCrime.query.with_entities(WarCrime.category).distinct().order_by(WarCrime.category).all()]

    data = []
    for event in events:
        data.append({
            'id': event.id,
            'title': event.title,
            'event_date': event.event_date.isoformat() if event.event_date else None,
            'end_date': event.end_date.isoformat() if event.end_date else None,
            'location': event.location,
            'region': event.region,
            'perpetrators': event.perpetrators,
            'victims': event.victims,
            'death_toll': event.death_toll,
            'category': event.category,
            'description': event.description,
            'sources': event.sources,
            'media_url': event.media_url,
        })

    return jsonify({
        'events': data,
        'categories': categories,
    })

