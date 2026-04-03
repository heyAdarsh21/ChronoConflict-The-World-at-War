"""Strategic advisor service — intelligence-driven decision support system that analyses
the current simulation state and recommends optimal decisions with risk assessments."""

from __future__ import annotations

from datetime import datetime

from src.ww2ops.db.models import (
    Battle,
    GeographicRegion,
    IntelligenceReport,
    Nation,
    Operation,
    ResourceBalance,
    ResourceSnapshot,
    Simulation,
)


class StrategicAdvisorService:
    """Provides AI-driven strategic recommendations for simulation decisions."""

    # Seasonal campaign effectiveness windows
    CAMPAIGN_SEASONS = {
        "Europe": {"best": [5, 6, 7, 8], "worst": [12, 1, 2], "reason_best": "Summer campaigning weather", "reason_worst": "Winter conditions degrade mobility and logistics"},
        "Eastern Front": {"best": [6, 7, 8], "worst": [11, 12, 1, 2], "reason_best": "Brief dry summer window", "reason_worst": "Russian winter destroys unprepared armies"},
        "Africa": {"best": [10, 11, 12, 1, 2], "worst": [6, 7, 8], "reason_best": "Cooler temperatures improve operations", "reason_worst": "Extreme heat degrades equipment and personnel"},
        "Pacific": {"best": [1, 2, 3, 4], "worst": [7, 8, 9], "reason_best": "Calmer seas for amphibious operations", "reason_worst": "Typhoon season threatens naval operations"},
        "Asia": {"best": [11, 12, 1, 2], "worst": [6, 7, 8, 9], "reason_best": "Dry season enables movement", "reason_worst": "Monsoon season makes jungle operations impossible"},
    }

    def get_recommendations(self, simulation_id: int) -> dict:
        """Generate strategic recommendations for the current simulation state."""
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return {"error": "Simulation not found"}

        year = min(max(simulation.start_year + simulation.current_turn, 1939), 1945)
        month = min(max(simulation.current_turn, 1), 12)
        coalition_nations = Nation.query.filter_by(side=simulation.side).all()

        # Analyse current resource state
        resource_analysis = self._analyse_resources(coalition_nations, simulation, year)
        # Analyse theater conditions
        theater_analysis = self._analyse_theaters(simulation.side, year, month)
        # Generate recommendations
        recommendations = self._generate_recommendations(
            simulation, resource_analysis, theater_analysis, year, month
        )
        # Risk assessment
        risk_matrix = self._build_risk_matrix(simulation, resource_analysis, year)

        return {
            "simulation_id": simulation_id,
            "scenario_year": year,
            "scenario_month": month,
            "current_turn": simulation.current_turn,
            "side": simulation.side,
            "resource_summary": resource_analysis,
            "theater_conditions": theater_analysis,
            "recommendations": recommendations,
            "risk_matrix": risk_matrix,
            "strategic_context": self._strategic_context(simulation.side, year),
        }

    def _analyse_resources(self, nations: list, simulation: Simulation, year: int) -> dict:
        """Analyse coalition resource state."""
        totals = {"oil": 0.0, "steel": 0.0, "manpower": 0.0, "food": 0.0, "ammunition": 0.0, "aircraft": 0.0}
        morale_values = []
        cinc_total = 0.0
        nation_count = 0

        for nation in nations:
            # Check simulation-specific snapshots first, then historical
            snapshot = (
                ResourceSnapshot.query.filter_by(nation_id=nation.id, simulation_id=simulation.id)
                .order_by(ResourceSnapshot.snapshot_date.desc())
                .first()
            )
            if not snapshot:
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

            nation_count += 1
            balances = {b.resource_type.code: float(b.amount) for b in snapshot.balances}
            for key in totals:
                totals[key] += balances.get(key, 0)

            metrics = snapshot.metrics or {}
            if metrics.get("morale") is not None:
                morale_values.append(float(metrics["morale"]))
            cinc_total += float(metrics.get("cinc", 0))

        avg_morale = sum(morale_values) / max(len(morale_values), 1) if morale_values else 50
        # Identify critical shortages
        shortages = []
        if totals["oil"] < 3000:
            shortages.append({"resource": "oil", "severity": "critical", "recommendation": "Prioritise fuel supply through diplomatic trade or resource allocation"})
        if totals["ammunition"] < 50:
            shortages.append({"resource": "ammunition", "severity": "warning", "recommendation": "Shift industrial production towards ordnance"})
        if totals["manpower"] < 2000000:
            shortages.append({"resource": "manpower", "severity": "warning", "recommendation": "Consider defensive posture to conserve personnel"})
        if avg_morale < 40:
            shortages.append({"resource": "morale", "severity": "critical", "recommendation": "Undertake a low-risk operation to boost morale before major offensives"})

        return {
            "coalition_strength": {k: round(v, 1) for k, v in totals.items()},
            "average_morale": round(avg_morale, 1),
            "composite_capability_index": round(cinc_total, 4),
            "nation_count": nation_count,
            "shortages": shortages,
            "overall_readiness": "strong" if not shortages else ("degraded" if len(shortages) <= 2 else "critical"),
        }

    def _analyse_theaters(self, side: str, year: int, month: int) -> list[dict]:
        """Analyse each geographic theater's suitability for operations."""
        theaters = []
        regions = GeographicRegion.query.filter(GeographicRegion.strategic_rating.is_not(None)).all()
        rated_theaters = {}

        for region in regions:
            theater = region.theater or "Europe"
            if theater not in rated_theaters or region.strategic_rating > rated_theaters[theater]["rating"]:
                rated_theaters[theater] = {"rating": region.strategic_rating or 5, "region": region.name}

        for theater, info in rated_theaters.items():
            season_data = self.CAMPAIGN_SEASONS.get(theater, self.CAMPAIGN_SEASONS["Europe"])
            if month in season_data.get("best", []):
                season_status = "optimal"
                season_reason = season_data["reason_best"]
            elif month in season_data.get("worst", []):
                season_status = "adverse"
                season_reason = season_data["reason_worst"]
            else:
                season_status = "acceptable"
                season_reason = "Standard campaigning conditions"

            # Count historical operations in this theater
            op_count = Operation.query.filter_by(side=side).join(Operation.region).filter(
                GeographicRegion.theater == theater
            ).count()

            theaters.append({
                "theater": theater,
                "strategic_rating": info["rating"],
                "key_region": info["region"],
                "season_status": season_status,
                "season_reason": season_reason,
                "historical_operations": op_count,
                "recommended_action": self._theater_recommendation(theater, season_status, year, side),
            })

        theaters.sort(key=lambda t: t["strategic_rating"], reverse=True)
        return theaters

    def _theater_recommendation(self, theater: str, season: str, year: int, side: str) -> str:
        if season == "adverse":
            return f"Avoid major offensive operations in {theater} — conditions unfavourable. Consider defensive consolidation or operations in other theaters."
        if season == "optimal":
            return f"{theater} conditions are optimal for offensive operations. Recommend concentrating forces for a decisive campaign."
        return f"Conditions in {theater} are acceptable. Operations feasible but consider seasonal windows in other theaters."

    def _generate_recommendations(self, simulation: Simulation, resources: dict, theaters: list, year: int, month: int) -> list[dict]:
        """Generate prioritised list of recommended actions."""
        recommendations = []
        readiness = resources.get("overall_readiness", "strong")

        # Recommendation 1: Based on resource state
        if readiness == "critical":
            recommendations.append({
                "priority": 1,
                "type": "resource_allocation",
                "title": "Emergency Resource Mobilisation",
                "description": "Critical resource shortages detected. Recommend immediate industrial reallocation to address deficiencies before considering offensive operations.",
                "risk_level": "low",
                "confidence": 0.85,
                "suggested_params": {"resource": resources["shortages"][0]["resource"] if resources["shortages"] else "steel", "amount": 10000},
            })
        elif readiness == "degraded":
            recommendations.append({
                "priority": 2,
                "type": "resource_allocation",
                "title": "Targeted Resource Programme",
                "description": f"Address identified shortages ({', '.join(s['resource'] for s in resources['shortages'])}) through targeted allocation.",
                "risk_level": "low",
                "confidence": 0.78,
                "suggested_params": {"resource": resources["shortages"][0]["resource"] if resources["shortages"] else "oil", "amount": 5000},
            })

        # Recommendation 2: Based on theater conditions
        optimal_theaters = [t for t in theaters if t["season_status"] == "optimal"]
        if optimal_theaters and readiness != "critical":
            best = optimal_theaters[0]
            recommendations.append({
                "priority": 1 if readiness == "strong" else 3,
                "type": "military_action",
                "title": f"Offensive in {best['theater']}",
                "description": f"Conditions in {best['theater']} ({best['key_region']}) are optimal. {best['season_reason']}. Strategic rating: {best['strategic_rating']}/10.",
                "risk_level": "medium",
                "confidence": 0.72,
                "suggested_params": {"operation_type": "offensive", "location": best["key_region"], "forces": 12000},
            })

        # Recommendation 3: Intelligence gathering
        intel_count = IntelligenceReport.query.filter(
            IntelligenceReport.nation.has(side=simulation.side)
        ).count()
        if intel_count < 5 or simulation.current_turn <= 2:
            recommendations.append({
                "priority": 2,
                "type": "espionage",
                "title": "Intelligence Collection Campaign",
                "description": "Insufficient intelligence on enemy dispositions. Recommend signals intelligence and reconnaissance operations before committing to major offensives.",
                "risk_level": "medium",
                "confidence": 0.70,
                "suggested_params": {"target": "axis" if simulation.side == "allies" else "allies", "mission_type": "signals_intelligence"},
            })

        # Recommendation 4: Diplomacy (if coalition is thin)
        if resources.get("nation_count", 0) < 4:
            recommendations.append({
                "priority": 3,
                "type": "diplomacy",
                "title": "Coalition Expansion",
                "description": "Coalition lacks depth. Diplomatic engagement with potential allies would strengthen the war effort and secure additional resources.",
                "risk_level": "low",
                "confidence": 0.65,
                "suggested_params": {"action": "alliance_negotiation"},
            })

        # Sort by priority
        recommendations.sort(key=lambda r: r["priority"])
        return recommendations

    def _build_risk_matrix(self, simulation: Simulation, resources: dict, year: int) -> dict:
        """Build a risk assessment matrix for each decision type."""
        readiness = resources.get("overall_readiness", "strong")
        morale = resources.get("average_morale", 50)

        return {
            "military_action": {
                "risk_level": "high" if readiness == "critical" else ("medium" if morale < 50 else "low"),
                "success_probability_range": [0.30, 0.75] if readiness != "critical" else [0.15, 0.45],
                "potential_upside": "Territory gained, morale boost, strategic initiative",
                "potential_downside": "Heavy casualties, morale loss, resource drain",
            },
            "espionage": {
                "risk_level": "medium",
                "success_probability_range": [0.35, 0.70],
                "potential_upside": "Intelligence gained, informed future decisions",
                "potential_downside": "Operative losses, compromised networks",
            },
            "resource_allocation": {
                "risk_level": "low",
                "success_probability_range": [0.55, 0.85],
                "potential_upside": "Improved production, strengthened logistics",
                "potential_downside": "Minor efficiency loss, opportunity cost",
            },
            "diplomacy": {
                "risk_level": "low",
                "success_probability_range": [0.40, 0.75],
                "potential_upside": "Alliance strengthened, resource access, coalition depth",
                "potential_downside": "Diplomatic setback, reduced influence",
            },
        }

    def _strategic_context(self, side: str, year: int) -> dict:
        """Provide strategic context for the current year."""
        contexts = {
            "allies": {
                1939: "The Allies are on the defensive. German Blitzkrieg has shattered Poland. Build strength and prepare for a long war.",
                1940: "France has fallen. Britain stands alone. Survival is the priority — build air defences and maintain Atlantic supply lines.",
                1941: "The war expands with Barbarossa and Pearl Harbor. New allies join but face initial setbacks. Build industrial capacity.",
                1942: "The year of turning points. Stalingrad and Midway present opportunities to seize the initiative.",
                1943: "Allied momentum builds. Consider peripheral campaigns (North Africa, Sicily) to weaken the Axis before opening a second front.",
                1944: "The time for decisive action. D-Day and Bagration can break the Axis on two fronts simultaneously.",
                1945: "The endgame. Concentrate overwhelming force for final campaigns. The Axis is collapsing.",
            },
            "axis": {
                1939: "Initiative belongs to the Axis. Exploit Blitzkrieg advantages before enemies mobilise.",
                1940: "Peak of expansion. But overextension risks grow. Secure conquered territories and neutralise Britain.",
                1941: "The gamble of Barbarossa. If the Soviet Union does not fall quickly, a two-front war becomes unsustainable.",
                1942: "Strategic overreach threatens. Stalingrad and Midway are critical — failure here shifts the war permanently.",
                1943: "The initiative is shifting. Fall back to defensive lines and husband resources for a protracted defence.",
                1944: "The Allies approach from all directions. Defensive genius and new weapons (V-weapons, jets) offer slim hope.",
                1945: "The war is effectively lost. Every decision prolongs suffering. Consider terms.",
            },
        }
        context_text = contexts.get(side, contexts["allies"]).get(year, f"Year {year} — assess the strategic situation.")
        return {
            "year": year,
            "side": side,
            "assessment": context_text,
            "phase": "early_war" if year <= 1941 else ("mid_war" if year <= 1943 else "late_war"),
        }
