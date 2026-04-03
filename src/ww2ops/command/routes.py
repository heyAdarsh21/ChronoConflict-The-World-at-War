from flask import Blueprint, render_template, request

from src.ww2ops.core.http import success_response
from src.ww2ops.services.command_service import CommandService

bp = Blueprint("command", __name__, url_prefix="/command")
service = CommandService()


@bp.route("/")
def index():
    return render_template("command/index.html")


@bp.route("/api/leaders")
def leaders():
    return success_response(service.list_leaders(country=request.args.get("country"), role_type=request.args.get("role_type"), search=request.args.get("q"), page=request.args.get("page", 1, type=int), per_page=request.args.get("per_page", 12, type=int)))


@bp.route("/api/leaders/<int:leader_id>")
def leader_detail(leader_id: int):
    return success_response(service.get_leader(leader_id))
