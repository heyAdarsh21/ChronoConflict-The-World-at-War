from flask import Blueprint, render_template, request

from src.ww2ops.core.http import success_response
from src.ww2ops.services.aftermath_service import AftermathService

bp = Blueprint("aftermath", __name__, url_prefix="/aftermath")
service = AftermathService()


@bp.route("/")
def index():
    return render_template("aftermath/index.html")


@bp.route("/api/events")
def events():
    return success_response(service.list_events(category=request.args.get("category"), start_year=request.args.get("start_year", type=int), end_year=request.args.get("end_year", type=int), region=request.args.get("region")))
