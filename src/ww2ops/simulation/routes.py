import json
from http import HTTPStatus

from flask import Blueprint, redirect, render_template, session, url_for
from pydantic import ValidationError

from src.ww2ops.core.http import error_response, success_response, validation_error_response
from src.ww2ops.core.validation import parse_json
from src.ww2ops.db.models import Simulation
from src.ww2ops.schemas.requests import DecisionRequest, StartSimulationRequest
from src.ww2ops.services.counterfactual_service import CounterfactualService
from src.ww2ops.services.simulation_service import SimulationService
from src.ww2ops.services.strategic_advisor_service import StrategicAdvisorService

bp = Blueprint("simulation", __name__, url_prefix="/simulation")
service = SimulationService()
counterfactual_service = CounterfactualService()
advisor_service = StrategicAdvisorService()

# ── Pre-built Scenarios ───────────────────────────────────────────────────

SCENARIOS = [
    {"id": "overlord_allied", "name": "Operation Overlord — Allied Perspective", "description": "Command the Allied invasion of Normandy. Land on the beaches of France and liberate Western Europe.", "start_year": 1944, "side": "allies", "difficulty": "medium", "historical_context": "June 1944: The largest amphibious invasion in history."},
    {"id": "barbarossa_axis", "name": "Operation Barbarossa — Axis Gamble", "description": "Lead the Axis invasion of the Soviet Union. Can you succeed where history says you failed?", "start_year": 1941, "side": "axis", "difficulty": "hard", "historical_context": "June 1941: 3.8 million Axis troops invade along a 2,900 km front."},
    {"id": "stalingrad_allied", "name": "Defence of Stalingrad", "description": "Hold the city that bears Stalin's name. Survive the siege and launch the decisive counteroffensive.", "start_year": 1942, "side": "allies", "difficulty": "hard", "historical_context": "August 1942: The bloodiest battle in human history begins."},
    {"id": "midway_allied", "name": "Battle of Midway — Pacific Turning Point", "description": "Command the U.S. Pacific Fleet. Use intelligence to ambush the Japanese carrier force.", "start_year": 1942, "side": "allies", "difficulty": "medium", "historical_context": "June 1942: Codebreakers identify the Japanese target."},
    {"id": "africa_allied", "name": "North African Campaign", "description": "Lead Allied forces from El Alamein to Tunisia. Desert warfare against the legendary Afrika Korps.", "start_year": 1942, "side": "allies", "difficulty": "medium", "historical_context": "October 1942: Montgomery prepares his offensive at El Alamein."},
    {"id": "berlin_allied", "name": "Race to Berlin", "description": "Command the final Allied push into the heart of Nazi Germany. End the war in Europe.", "start_year": 1945, "side": "allies", "difficulty": "easy", "historical_context": "January 1945: The Red Army launches the Vistula-Oder Offensive."},
    {"id": "atlantic_allied", "name": "Battle of the Atlantic", "description": "Protect the vital Atlantic convoy routes against German U-boat wolfpacks.", "start_year": 1942, "side": "allies", "difficulty": "hard", "historical_context": "1942: The 'Second Happy Time' — U-boats devastate Allied shipping."},
    {"id": "pacific_island", "name": "Island-Hopping Campaign", "description": "Lead the Pacific island-hopping campaign from Guadalcanal to Okinawa.", "start_year": 1943, "side": "allies", "difficulty": "medium", "historical_context": "1943: The long road to Tokyo begins."},
]


@bp.route("/")
def index():
    return render_template("simulation/index.html")


@bp.route("/start", methods=["POST"])
def start():
    if "user_id" not in session:
        return error_response("Not authenticated", HTTPStatus.UNAUTHORIZED)
    try:
        payload = parse_json(StartSimulationRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    simulation = service.start_simulation(session["user_id"], payload.scenario_name, payload.start_year, payload.side, payload.seed)
    return success_response({
        "simulation_id": simulation.id,
        "scenario_name": simulation.scenario_name,
        "start_year": simulation.start_year,
        "side": simulation.side,
        "seed": simulation.seed,
    }, HTTPStatus.CREATED)


@bp.route("/decision", methods=["POST"])
def decision():
    if "user_id" not in session:
        return error_response("Not authenticated", HTTPStatus.UNAUTHORIZED)
    try:
        payload = parse_json(DecisionRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    try:
        simulation = service.get_simulation_for_user(payload.simulation_id, session["user_id"])
    except LookupError:
        return error_response("Simulation not found", HTTPStatus.NOT_FOUND)

    decision_row, result = service.process_decision(simulation, payload.decision_type, payload.decision_data)
    return success_response({
        "success": True,
        "outcome": result,
        "decision_id": decision_row.id,
        "simulation_id": simulation.id,
    })


@bp.route("/<int:simulation_id>")
def view(simulation_id: int):
    simulation = Simulation.query.get(simulation_id)
    if not simulation:
        return redirect(url_for("simulation.index"))

    decision_map = {outcome.decision_id: outcome for outcome in simulation.outcomes}
    simulation.decisions_json = json.dumps([
        {
            "type": decision.decision_type,
            "timestamp": decision.created_at.isoformat(),
            "outcome": decision_map[decision.id].impact_payload if decision.id in decision_map else {"success": False, "message": "No outcome available."},
        }
        for decision in simulation.decisions
    ])
    return render_template("simulation/view.html", simulation=simulation)


# ── New Endpoints ─────────────────────────────────────────────────────────

@bp.route("/scenarios")
def scenarios():
    """List pre-built simulation scenarios."""
    return success_response(SCENARIOS)


@bp.route("/<int:simulation_id>/advisor")
def advisor(simulation_id: int):
    """Get strategic advisor recommendations for a simulation."""
    return success_response(advisor_service.get_recommendations(simulation_id))


@bp.route("/<int:simulation_id>/divergence")
def divergence(simulation_id: int):
    """Get counterfactual divergence analysis for a simulation."""
    return success_response(counterfactual_service.get_simulation_divergence(simulation_id))
