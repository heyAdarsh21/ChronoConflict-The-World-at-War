from flask import Blueprint, render_template, request

from src.ww2ops.core.http import success_response
from src.ww2ops.services.timeline_service import TimelineService

bp = Blueprint('timeline', __name__, url_prefix='/timeline')
service = TimelineService()


@bp.route('/')
def index():
    return render_template('timeline/index.html')


@bp.route('/api/events')
def events():
    start_year = request.args.get('start_year', 1939, type=int)
    end_year = request.args.get('end_year', 1945, type=int)
    simulation_id = request.args.get('simulation_id', type=int)
    return success_response(service.list_events(start_year, end_year, simulation_id=simulation_id))
