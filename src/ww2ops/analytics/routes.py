from flask import Blueprint, render_template, request

from src.ww2ops.core.http import success_response
from src.ww2ops.db.models import Battle, GeographicRegion, Nation, ResourceBalance, ResourceSnapshot, ResourceType
from src.ww2ops.services.dashboard_service import DashboardService
from src.ww2ops.services.timeline_service import TimelineService

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
analytics_bp = Blueprint('analytics_api', __name__, url_prefix='/analytics')
service = DashboardService()
timeline_service = TimelineService()


@bp.route('/')
def index():
    return render_template('dashboard/index.html')


@bp.route('/api/resources')
def resource_overview():
    return success_response(service.get_resource_overview())


@bp.route('/api/territories')
def territories():
    return success_response(service.get_territory_overview())


@bp.route('/api/intelligence')
def intelligence():
    return success_response(service.get_recent_intelligence())


@bp.route('/api/battles')
def battles():
    return success_response(service.get_battles())


def build_analytics_payload():
    return {
        'stats': service.get_stats(),
        'resources': service.get_resource_overview(),
        'latest_battles': service.get_battles()[:5],
        'recent_intelligence': service.get_recent_intelligence()[:5],
        'timeline': timeline_service.list_events(1939, 1945)[:12],
    }


@analytics_bp.route('/')
def analytics_index():
    return success_response(build_analytics_payload())


@analytics_bp.route('/overview')
def analytics_overview():
    return success_response(build_analytics_payload())


# ── New Analytics Endpoints ───────────────────────────────────────────────

@analytics_bp.route('/war-progress')
def war_progress():
    """Track war progress year by year — resource totals, battle outcomes, territorial changes."""
    progress = []
    for year in range(1939, 1946):
        from datetime import datetime
        start_dt = datetime(year, 1, 1)
        end_dt = datetime(year, 12, 31)

        # Resource totals by side
        allied_totals = _resource_totals_for_side("allies", year)
        axis_totals = _resource_totals_for_side("axis", year)

        # Battle statistics for this year
        battles = Battle.query.filter(
            Battle.start_date >= start_dt,
            Battle.start_date <= end_dt,
        ).all()
        allied_victories = sum(1 for b in battles if b.victor_side == "allies")
        axis_victories = sum(1 for b in battles if b.victor_side == "axis")
        total_casualties = sum(
            (b.axis_casualties or 0) + (b.allied_casualties or 0) for b in battles
        )

        progress.append({
            "year": year,
            "allied_resources": allied_totals,
            "axis_resources": axis_totals,
            "battles_fought": len(battles),
            "allied_victories": allied_victories,
            "axis_victories": axis_victories,
            "total_casualties": total_casualties,
            "battle_names": [b.name for b in battles],
        })

    return success_response(progress)


@analytics_bp.route('/force-balance')
def force_balance():
    """Compare Axis vs Allied military strength over time."""
    balance_data = []
    for year in range(1939, 1946):
        allied = _aggregate_metrics_for_side("allies", year)
        axis = _aggregate_metrics_for_side("axis", year)
        balance_data.append({
            "year": year,
            "allied": allied,
            "axis": axis,
            "balance_ratio": round(allied.get("composite_strength", 1) / max(axis.get("composite_strength", 1), 0.01), 3),
        })
    return success_response(balance_data)


@analytics_bp.route('/theater-analysis')
def theater_analysis():
    """Theater-by-theater breakdown of battles, operations, and casualties."""
    theaters = {}
    battles = Battle.query.all()
    for battle in battles:
        theater = "Unknown"
        if battle.region:
            theater = battle.region.theater or battle.region.name
        if theater not in theaters:
            theaters[theater] = {
                "theater": theater,
                "total_battles": 0,
                "allied_victories": 0,
                "axis_victories": 0,
                "total_axis_casualties": 0,
                "total_allied_casualties": 0,
                "key_battles": [],
            }
        t = theaters[theater]
        t["total_battles"] += 1
        if battle.victor_side == "allies":
            t["allied_victories"] += 1
        elif battle.victor_side == "axis":
            t["axis_victories"] += 1
        t["total_axis_casualties"] += battle.axis_casualties or 0
        t["total_allied_casualties"] += battle.allied_casualties or 0
        t["key_battles"].append({
            "name": battle.name,
            "year": battle.start_date.year if battle.start_date else None,
            "victor": battle.victor_side,
        })

    return success_response(list(theaters.values()))


# ── Helpers ───────────────────────────────────────────────────────────────

def _resource_totals_for_side(side: str, year: int) -> dict:
    from datetime import datetime
    nations = Nation.query.filter_by(side=side).all()
    totals = {}
    for nation in nations:
        snapshot = (
            ResourceSnapshot.query.filter(
                ResourceSnapshot.nation_id == nation.id,
                ResourceSnapshot.simulation_id.is_(None),
                ResourceSnapshot.snapshot_date <= datetime(year, 12, 31),
            )
            .order_by(ResourceSnapshot.snapshot_date.desc())
            .first()
        )
        if not snapshot:
            continue
        for balance in snapshot.balances:
            code = balance.resource_type.code if balance.resource_type else "unknown"
            totals[code] = totals.get(code, 0) + float(balance.amount)
    return {k: round(v, 1) for k, v in totals.items()}


def _aggregate_metrics_for_side(side: str, year: int) -> dict:
    from datetime import datetime
    nations = Nation.query.filter_by(side=side).all()
    total_manpower = 0.0
    total_oil = 0.0
    total_steel = 0.0
    total_aircraft = 0.0
    cinc_sum = 0.0
    morale_values = []

    for nation in nations:
        snapshot = (
            ResourceSnapshot.query.filter(
                ResourceSnapshot.nation_id == nation.id,
                ResourceSnapshot.simulation_id.is_(None),
                ResourceSnapshot.snapshot_date <= datetime(year, 12, 31),
            )
            .order_by(ResourceSnapshot.snapshot_date.desc())
            .first()
        )
        if not snapshot:
            continue
        balances = {b.resource_type.code: float(b.amount) for b in snapshot.balances if b.resource_type}
        total_manpower += balances.get("manpower", 0)
        total_oil += balances.get("oil", 0)
        total_steel += balances.get("steel", 0)
        total_aircraft += balances.get("aircraft", 0)
        metrics = snapshot.metrics or {}
        cinc_sum += float(metrics.get("cinc", 0))
        if metrics.get("morale") is not None:
            morale_values.append(float(metrics["morale"]))

    composite = cinc_sum * 100 + total_manpower / 100000 + total_oil / 1000 + total_aircraft / 100
    return {
        "total_manpower": int(total_manpower),
        "total_oil": round(total_oil, 1),
        "total_steel": round(total_steel, 1),
        "total_aircraft": int(total_aircraft),
        "cinc_sum": round(cinc_sum, 4),
        "average_morale": round(sum(morale_values) / max(len(morale_values), 1), 1) if morale_values else 0,
        "composite_strength": round(composite, 2),
    }
