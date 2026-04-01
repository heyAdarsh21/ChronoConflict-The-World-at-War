"""
Command & Leadership routes
"""

from flask import Blueprint, render_template, jsonify, request
from models import Leader, CommandAssignment, Operation, Campaign

bp = Blueprint('command', __name__, url_prefix='/command')


@bp.route('/')
def index():
    """Command & Leadership main view"""
    return render_template('command/index.html')


@bp.route('/api/leaders')
def list_leaders():
    """List leaders with optional filters"""
    country = request.args.get('country')
    role_type = request.args.get('role_type')
    search = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    base_query = Leader.query
    countries = [row[0] for row in base_query.with_entities(Leader.country).distinct().order_by(Leader.country).all()]

    query = base_query
    if country:
        query = query.filter(Leader.country.ilike(f"%{country}%"))
    if role_type:
        query = query.filter(Leader.role_type == role_type)
    if search:
        like_term = f"%{search}%"
        query = query.filter(Leader.name.ilike(like_term) | Leader.biography.ilike(like_term))

    pagination = query.order_by(Leader.influence_score.desc().nullslast()).paginate(page=page, per_page=per_page, error_out=False)

    leaders_data = []
    for leader in pagination.items:
        leaders_data.append({
            'id': leader.id,
            'name': leader.name,
            'country': leader.country,
            'title': leader.title,
            'role_type': leader.role_type,
            'portrait_url': leader.portrait_url,
            'influence_score': leader.influence_score or 0,
            'key_operations': leader.key_operations,
        })

    return jsonify({
        'leaders': leaders_data,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'countries': countries,
    })


@bp.route('/api/leaders/<int:leader_id>')
def leader_detail(leader_id: int):
    """Return detailed leader dossier"""
    leader = Leader.query.get_or_404(leader_id)

    assignments_data = []
    for assignment in leader.assignments:
        context = None
        if assignment.operation:
            op = assignment.operation
            context = {
                'type': 'operation',
                'id': op.id,
                'name': op.name,
                'code_name': op.code_name,
                'start_date': op.start_date.isoformat() if op.start_date else None,
                'end_date': op.end_date.isoformat() if op.end_date else None,
                'outcome': op.outcome,
                'region': op.region,
            }
        elif assignment.campaign:
            camp = assignment.campaign
            context = {
                'type': 'campaign',
                'id': camp.id,
                'name': camp.name,
                'theater': camp.theater,
                'start_date': camp.start_date.isoformat() if camp.start_date else None,
                'end_date': camp.end_date.isoformat() if camp.end_date else None,
                'outcome': camp.outcome,
            }

        assignments_data.append({
            'id': assignment.id,
            'position': assignment.position,
            'start_date': assignment.start_date.isoformat() if assignment.start_date else None,
            'end_date': assignment.end_date.isoformat() if assignment.end_date else None,
            'notes': assignment.notes,
            'context': context,
        })

    data = {
        'id': leader.id,
        'name': leader.name,
        'country': leader.country,
        'title': leader.title,
        'role_type': leader.role_type,
        'biography': leader.biography,
        'ideology': leader.ideology,
        'portrait_url': leader.portrait_url,
        'notable_quotes': leader.notable_quotes,
        'key_operations': leader.key_operations,
        'influence_score': leader.influence_score,
        'assignments': assignments_data,
    }

    return jsonify(data)

