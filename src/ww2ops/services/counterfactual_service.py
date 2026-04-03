"""Counterfactual analysis service — compares simulation outcomes against historical record
and provides divergence analysis, alternative history narratives, and probability assessments."""

from __future__ import annotations

from datetime import datetime

from src.ww2ops.db.models import Battle, Nation, Operation, Simulation, SimulationDecision, SimulationOutcome


class CounterfactualService:
    """Analyses how simulation decisions diverge from historical WWII outcomes."""

    HISTORICAL_ANCHORS = {
        "Battle of Stalingrad": {"year": 1942, "victor": "allies", "probability": 0.55, "casualties_axis": 868000, "casualties_allied": 1130000, "significance": "Turning point of the Eastern Front"},
        "Battle of Midway": {"year": 1942, "victor": "allies", "probability": 0.40, "significance": "Turning point of the Pacific War"},
        "Battle of Normandy": {"year": 1944, "victor": "allies", "probability": 0.72, "casualties_axis": 200000, "casualties_allied": 226000, "significance": "Opening of the Western Front"},
        "Battle of Kursk": {"year": 1943, "victor": "allies", "probability": 0.68, "significance": "Last major German offensive in the East"},
        "Battle of Britain": {"year": 1940, "victor": "allies", "probability": 0.58, "significance": "Prevented German invasion of Britain"},
        "Battle of the Bulge": {"year": 1944, "victor": "allies", "probability": 0.65, "significance": "Germany's last Western offensive"},
        "Second Battle of El Alamein": {"year": 1942, "victor": "allies", "probability": 0.73, "significance": "First major British land victory"},
    }

    YEAR_PHASE_DESCRIPTORS = {
        1939: "The war's opening phase — Germany's Blitzkrieg dominates",
        1940: "Axis expansion at its peak — France falls, Britain stands alone",
        1941: "The war globalises — Barbarossa and Pearl Harbor",
        1942: "The turning point year — Stalingrad, Midway, El Alamein",
        1943: "Allied momentum builds — Kursk, Sicily, island-hopping begins",
        1944: "Liberation campaigns — D-Day, Bagration, Philippine Sea",
        1945: "Final campaigns — Berlin falls, atomic weapons end the Pacific war",
    }

    def get_simulation_divergence(self, simulation_id: int) -> dict:
        """Analyse all decisions in a simulation and compute cumulative divergence."""
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return {"error": "Simulation not found"}

        decisions = (
            SimulationDecision.query.filter_by(simulation_id=simulation_id)
            .order_by(SimulationDecision.turn_number.asc())
            .all()
        )
        outcomes = {o.decision_id: o for o in SimulationOutcome.query.filter_by(simulation_id=simulation_id).all()}

        cumulative_divergence = 0.0
        decision_analyses = []
        historical_comparison_battles = []

        for decision in decisions:
            outcome = outcomes.get(decision.id)
            if not outcome:
                continue

            year = min(max(simulation.start_year + decision.turn_number - 1, 1939), 1945)
            hist_prob = self._historical_probability(decision.decision_type, simulation.side, year)

            divergence = abs(outcome.success_probability - hist_prob)
            if outcome.realized_success != (hist_prob >= 0.5):
                divergence *= 1.5
            cumulative_divergence += divergence

            # Find closest historical battle for comparison
            closest_battle = self._find_closest_historical_anchor(year, decision.decision_type)

            analysis = {
                "turn": decision.turn_number,
                "decision_type": decision.decision_type,
                "success": outcome.realized_success,
                "probability": outcome.success_probability,
                "historical_baseline": round(hist_prob, 4),
                "divergence": round(divergence, 4),
                "narrative": outcome.narrative_summary,
                "year": year,
                "phase": self.YEAR_PHASE_DESCRIPTORS.get(year, f"Year {year}"),
            }
            if closest_battle:
                analysis["historical_parallel"] = closest_battle
            decision_analyses.append(analysis)

        # Determine timeline classification
        timeline_class = self._classify_timeline(cumulative_divergence, len(decisions))

        return {
            "simulation_id": simulation_id,
            "scenario_name": simulation.scenario_name,
            "side": simulation.side,
            "start_year": simulation.start_year,
            "total_decisions": len(decisions),
            "cumulative_divergence": round(cumulative_divergence, 4),
            "timeline_classification": timeline_class,
            "decisions": decision_analyses,
            "alternative_history_summary": self._generate_alt_history_summary(
                simulation.side, simulation.start_year, cumulative_divergence, decision_analyses
            ),
        }

    def _historical_probability(self, decision_type: str, side: str, year: int) -> float:
        """Return baseline probability for a decision type at a given year."""
        if decision_type == "military_action":
            if side == "allies":
                if year <= 1941:
                    return 0.30
                if year <= 1943:
                    return 0.52
                return 0.78
            else:
                if year <= 1941:
                    return 0.80
                if year <= 1943:
                    return 0.45
                return 0.18
        if decision_type == "espionage":
            return 0.65 if side == "allies" else 0.42
        if decision_type == "diplomacy":
            return 0.60 if side == "allies" else 0.50
        return 0.50

    def _find_closest_historical_anchor(self, year: int, decision_type: str) -> dict | None:
        """Find a real historical battle closest to the simulation's year."""
        best = None
        best_distance = 999
        for name, data in self.HISTORICAL_ANCHORS.items():
            distance = abs(data["year"] - year)
            if distance < best_distance:
                best_distance = distance
                best = {"name": name, "year": data["year"], "victor": data["victor"], "significance": data["significance"]}
        return best

    def _classify_timeline(self, divergence: float, decision_count: int) -> dict:
        avg = divergence / max(decision_count, 1)
        if avg < 0.08:
            label = "Historical"
            description = "This simulation closely mirrors actual WWII outcomes."
        elif avg < 0.18:
            label = "Plausible Alternative"
            description = "Minor deviations — an alternative course the war could conceivably have taken."
        elif avg < 0.30:
            label = "Counterfactual"
            description = "Significant divergence from history — a recognisable but altered WWII."
        elif avg < 0.50:
            label = "Radical Alternative"
            description = "Major departure from historical events — the war unfolds very differently."
        else:
            label = "Speculative Fiction"
            description = "Extreme divergence — this bears little resemblance to actual WWII history."
        return {"label": label, "description": description, "average_divergence": round(avg, 4)}

    def _generate_alt_history_summary(self, side: str, start_year: int, divergence: float, decisions: list[dict]) -> str:
        successes = sum(1 for d in decisions if d["success"])
        failures = len(decisions) - successes
        side_name = "Allied" if side == "allies" else "Axis"

        if divergence < 0.5:
            return f"The {side_name} coalition's {start_year} campaign follows a trajectory broadly consistent with historical patterns. {successes} successful operations and {failures} setbacks mirror the fortunes of war."
        if divergence < 1.5:
            return f"The {side_name} campaign diverges from history at several critical junctures. With {successes} successes against {failures} failures, the war takes a recognisably different path. Key decision points created ripple effects that altered the strategic balance."
        return f"The {side_name} campaign represents a radical departure from historical WWII. {successes} successes and {failures} failures created a cascading series of divergences. The resulting alternative history would be unrecognisable to anyone familiar with the actual course of events."
