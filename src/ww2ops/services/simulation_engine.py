"""Enhanced WWII simulation engine with fog-of-war, supply chain logic, weather/terrain
modifiers, fatigue/attrition tracking, counterfactual divergence, and rich narrative
generation.

The engine is deterministic by seed so every simulation is reproducible.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

# ── Weight profiles per decision type ─────────────────────────────────────

DECISION_WEIGHTS = {
    "resource_allocation": {
        "resource_index": 0.22,
        "leadership_index": 0.10,
        "morale": 0.12,
        "historical_success_rate": 0.14,
        "coalition_depth": 0.12,
        "supply_chain": 0.14,
        "weather_modifier": 0.06,
        "fatigue_modifier": 0.10,
    },
    "espionage": {
        "resource_index": 0.06,
        "leadership_index": 0.12,
        "morale": 0.08,
        "intelligence_index": 0.26,
        "target_alignment": 0.10,
        "historical_success_rate": 0.14,
        "fog_of_war": 0.14,
        "fatigue_modifier": 0.10,
    },
    "military_action": {
        "resource_index": 0.18,
        "leadership_index": 0.14,
        "morale": 0.10,
        "intelligence_index": 0.08,
        "historical_success_rate": 0.12,
        "theater_advantage": 0.08,
        "supply_chain": 0.12,
        "weather_modifier": 0.10,
        "fatigue_modifier": 0.08,
    },
    "diplomacy": {
        "resource_index": 0.06,
        "leadership_index": 0.20,
        "morale": 0.10,
        "historical_success_rate": 0.14,
        "target_alignment": 0.18,
        "coalition_depth": 0.14,
        "fog_of_war": 0.08,
        "fatigue_modifier": 0.10,
    },
}

# ── Season & theater modifiers ────────────────────────────────────────────

SEASON_MODIFIERS = {
    # (month_range_start, month_range_end): {theater: modifier}
    (12, 2): {"Europe": -0.15, "Eastern Front": -0.30, "Pacific": 0.0, "Africa": 0.05, "Asia": -0.05},
    (3, 5): {"Europe": 0.05, "Eastern Front": -0.05, "Pacific": 0.0, "Africa": 0.0, "Asia": -0.10},
    (6, 8): {"Europe": 0.10, "Eastern Front": 0.10, "Pacific": -0.05, "Africa": -0.10, "Asia": -0.15},
    (9, 11): {"Europe": 0.0, "Eastern Front": -0.10, "Pacific": 0.05, "Africa": 0.05, "Asia": 0.0},
}

TERRAIN_MODIFIERS = {
    "urban": {"military_action": -0.12, "espionage": 0.08},
    "mountain": {"military_action": -0.18, "espionage": -0.05},
    "jungle": {"military_action": -0.15, "espionage": -0.10},
    "desert": {"military_action": -0.08, "espionage": 0.05},
    "naval": {"military_action": 0.0, "espionage": -0.12},
    "plains": {"military_action": 0.05, "espionage": 0.0},
    "forest": {"military_action": -0.10, "espionage": 0.05},
}

# ── Historical counterfactual anchors ─────────────────────────────────────

HISTORICAL_OUTCOMES = {
    "military_action": {
        "allies": {
            (1939, 1941): {"success_rate": 0.25, "typical_casualties_rate": 0.22},
            (1942, 1943): {"success_rate": 0.52, "typical_casualties_rate": 0.18},
            (1944, 1945): {"success_rate": 0.78, "typical_casualties_rate": 0.14},
        },
        "axis": {
            (1939, 1941): {"success_rate": 0.82, "typical_casualties_rate": 0.10},
            (1942, 1943): {"success_rate": 0.45, "typical_casualties_rate": 0.16},
            (1944, 1945): {"success_rate": 0.18, "typical_casualties_rate": 0.25},
        },
    },
    "espionage": {
        "allies": {(1939, 1945): {"success_rate": 0.65}},
        "axis": {(1939, 1945): {"success_rate": 0.42}},
    },
}

# ── Narrative templates ───────────────────────────────────────────────────

NARRATIVES = {
    "military_action": {
        True: [
            "The offensive at {location} succeeded against expectations — coalition forces exploited a gap in the enemy line, advancing {territory_gained} sector(s). Casualties stood at {casualties:,} personnel, but morale surged (+{morale_impact}). Historical baseline suggested {historical:.0%} probability; actual probability was {probability:.0%}.",
            "Overwhelming firepower and coordinated logistics delivered victory at {location}. Intelligence assessments proved accurate—enemy reserves were committed elsewhere. {casualties:,} casualties sustained, {territory_gained} objective(s) secured.",
            "A decisive engagement near {location} saw coalition armour and infantry achieve breakthrough thanks to leadership index {leadership:.2f}. Supply lines held firm (supply factor {supply:.2f}). Weather conditions were {weather_desc}.",
        ],
        False: [
            "The offensive at {location} stalled under fierce resistance. {casualties:,} casualties incurred without significant gains. Leadership coordination faltered (index {leadership:.2f}); intelligence underestimated enemy defensive depth. Morale dropped by {morale_impact} points.",
            "Overextended supply lines (factor {supply:.2f}) and adverse {weather_desc} conditions degraded the assault near {location}. The coalition suffered {casualties:,} losses and failed to secure objectives. Historical patterns suggested only {historical:.0%} success probability.",
            "The attack near {location} collapsed after initial progress. Enemy counterattack exploited a salient, inflicting {casualties:,} casualties. Fatigue factor {fatigue:.2f} indicated troops were at diminished effectiveness.",
        ],
    },
    "espionage": {
        True: [
            "Intelligence operation targeting {target} succeeded. {intelligence_gained} actionable items recovered through {source_type}. Fog-of-war factor {fog:.2f} — enemy counterintelligence did not detect the operation.",
            "Codebreaking effort against {target} communications yielded {intelligence_gained} decrypts. Confidence level elevated to {probability:.0%}. Coalition intelligence network integrity maintained.",
        ],
        False: [
            "Espionage mission against {target} was compromised. {casualties} operative(s) lost. Enemy counterintelligence (fog factor {fog:.2f}) detected and rolled up the network. {intelligence_gained} partial intelligence salvaged.",
            "The operation targeting {target} failed — double agent suspected. {casualties} casualty(ies). Intelligence yield limited to {intelligence_gained} items of marginal value.",
        ],
    },
    "resource_allocation": {
        True: [
            "Resource reallocation succeeded — {resource} production shifted by {production:+,.0f} units. Industrial mobilisation index at {resource_index:.2f}. Coalition morale adjusted {morale:+d}.",
            "Strategic resource programme delivered results. {resource} output changed by {production:+,.0f} units with leadership oversight (index {leadership:.2f}) ensuring efficient conversion.",
        ],
        False: [
            "Resource allocation programme underperformed expectations. {resource} output changed by {production:+,.0f} units due to logistics bottlenecks (supply factor {supply:.2f}). Morale impact: {morale:+d}.",
            "Industrial conversion effort encountered supply chain disruptions. {resource} stocks shifted by {production:+,.0f} units. Worker fatigue (factor {fatigue:.2f}) degraded output quality.",
        ],
    },
    "diplomacy": {
        True: [
            "Diplomatic initiative with {target} succeeded — alliance strength increased by {alliance_strength}. Resource transfers of {resources_gained:,} units secured. Coalition depth expanded.",
            "Negotiations with {target} achieved a favourable accord. Trade agreements yielded {resources_gained:,} resource units. Coalition morale improved.",
        ],
        False: [
            "Diplomatic overture to {target} was rebuffed. Alliance cohesion weakened by {alliance_strength} points. No material gains achieved. Target alignment factor {alignment:.2f} was unfavourable.",
            "Negotiations with {target} collapsed — ideological differences proved insurmountable. Alliance strength decreased by {alliance_strength} and coalition morale dropped.",
        ],
    },
}


@dataclass
class SimulationInputs:
    seed: int
    turn_number: int
    decision_type: str
    decision_data: dict
    baseline: dict


@dataclass
class SimulationContext:
    """Extended context tracked across multiple turns within a simulation."""
    cumulative_casualties: int = 0
    turns_in_theater: int = 0
    previous_success: bool | None = None
    divergence_score: float = 0.0
    active_theaters: list[str] = field(default_factory=list)


class SimulationEngine:
    """Deterministic simulation engine with deep strategic modelling."""

    def evaluate(self, inputs: SimulationInputs, context: SimulationContext | None = None) -> dict:
        ctx = context or SimulationContext()
        rng = random.Random(f"{inputs.seed}:{inputs.turn_number}:{inputs.decision_type}:{inputs.decision_data}")

        factors = self._calculate_factors(inputs, ctx, rng)
        weights = DECISION_WEIGHTS.get(inputs.decision_type, DECISION_WEIGHTS["military_action"])
        weighted_score = sum(factors.get(name, 0.5) * weight for name, weight in weights.items())

        # Bounded perturbation
        noise = rng.gauss(0, 0.02)
        probability = max(0.05, min(0.95, weighted_score + noise))
        success = rng.random() <= probability

        monte_carlo = self._monte_carlo(probability, rng)
        impact = self._build_impact(inputs, success, probability, monte_carlo, ctx, factors)
        divergence = self._calculate_divergence(inputs, success, probability)
        scenarios = self._generate_follow_up_scenarios(inputs, success, impact, rng)

        narrative = self._generate_narrative(inputs, success, probability, factors, impact)

        return {
            "success": success,
            "probability": round(probability, 4),
            "weighted_score": round(weighted_score, 4),
            "factors": {k: round(v, 4) for k, v in factors.items()},
            "monte_carlo": monte_carlo,
            "impact": impact,
            "message": narrative,
            "divergence": divergence,
            "follow_up_scenarios": scenarios,
            **impact,
        }

    # ── Factor calculation ────────────────────────────────────────────────

    def _calculate_factors(self, inputs: SimulationInputs, ctx: SimulationContext, rng: random.Random) -> dict:
        baseline = inputs.baseline
        amount = float(inputs.decision_data.get("amount", 1000))
        forces = float(inputs.decision_data.get("forces", 5000))
        year = baseline.get("year", 1942)
        month = min(max(inputs.turn_number, 1), 12)

        resource_index = self._clamp(baseline.get("resource_index", 0.5) + min(amount / 250000, 0.12) + min(forces / 100000, 0.08))
        leadership_index = self._clamp(baseline.get("leadership_index", 0.5))
        morale = self._clamp(baseline.get("morale", 0.5))
        intelligence_index = self._clamp(baseline.get("intelligence_index", 0.5))
        historical_sr = self._clamp(baseline.get("historical_success_rate", 0.5))
        target_alignment = self._clamp(baseline.get("target_alignment", 0.5))
        theater_advantage = self._clamp(baseline.get("theater_advantage", 0.5))
        coalition_depth = self._clamp(baseline.get("coalition_depth", 0.5))

        # Fog of War — intelligence accuracy degrades with distance & counter-intel
        fog_base = intelligence_index * 0.6 + leadership_index * 0.2 + 0.2
        enemy_counter_intel = rng.uniform(0.15, 0.40)
        fog_of_war = self._clamp(fog_base - enemy_counter_intel)

        # Supply Chain — proximity to friendly supply depots
        supply_base = resource_index * 0.5 + coalition_depth * 0.3
        overextension = min(0.3, ctx.turns_in_theater * 0.05) if ctx.turns_in_theater > 2 else 0
        supply_chain = self._clamp(supply_base + 0.2 - overextension)

        # Weather & Terrain
        theater = (inputs.decision_data.get("location") or baseline.get("theater") or "Europe")
        weather_modifier = self._get_weather_modifier(theater, month)
        terrain = (inputs.decision_data.get("terrain") or "plains").lower()
        terrain_mod = TERRAIN_MODIFIERS.get(terrain, {}).get(inputs.decision_type, 0.0)
        weather_factor = self._clamp(0.5 + weather_modifier + terrain_mod)

        # Fatigue & Attrition
        fatigue_base = 0.7
        if ctx.cumulative_casualties > 50000:
            fatigue_base -= min(0.25, ctx.cumulative_casualties / 500000)
        if ctx.previous_success is False:
            fatigue_base -= 0.08
        elif ctx.previous_success is True:
            fatigue_base += 0.05
        fatigue_modifier = self._clamp(fatigue_base)

        return {
            "resource_index": resource_index,
            "leadership_index": leadership_index,
            "morale": morale,
            "intelligence_index": intelligence_index,
            "historical_success_rate": historical_sr,
            "target_alignment": target_alignment,
            "theater_advantage": theater_advantage,
            "coalition_depth": coalition_depth,
            "fog_of_war": fog_of_war,
            "supply_chain": supply_chain,
            "weather_modifier": weather_factor,
            "fatigue_modifier": fatigue_modifier,
        }

    def _get_weather_modifier(self, theater: str, month: int) -> float:
        for (start_month, end_month), modifiers in SEASON_MODIFIERS.items():
            if start_month <= end_month:
                in_range = start_month <= month <= end_month
            else:
                in_range = month >= start_month or month <= end_month
            if in_range:
                for key in modifiers:
                    if key.lower() in theater.lower() or theater.lower() in key.lower():
                        return modifiers[key]
                return modifiers.get("Europe", 0.0)
        return 0.0

    # ── Monte Carlo ───────────────────────────────────────────────────────

    def _monte_carlo(self, probability: float, rng: random.Random) -> dict:
        trials = 256
        successes = sum(1 for _ in range(trials) if rng.random() <= probability)
        return {
            "trials": trials,
            "successes": successes,
            "estimated_probability": round(successes / trials, 4),
            "confidence_interval_95": [
                round(max(0, successes / trials - 1.96 * math.sqrt(successes / trials * (1 - successes / trials) / trials)), 4),
                round(min(1, successes / trials + 1.96 * math.sqrt(successes / trials * (1 - successes / trials) / trials)), 4),
            ],
        }

    # ── Impact computation ────────────────────────────────────────────────

    def _build_impact(self, inputs: SimulationInputs, success: bool, probability: float, monte_carlo: dict, ctx: SimulationContext, factors: dict) -> dict:
        baseline = inputs.baseline
        coalition_resource_total = max(1.0, baseline.get("resource_total", 1000000))

        if inputs.decision_type == "resource_allocation":
            amount = float(inputs.decision_data.get("amount", 1000))
            efficiency = 0.04 + factors.get("leadership_index", 0.5) * 0.08 + factors.get("supply_chain", 0.5) * 0.06
            production_shift = round(amount * efficiency * (1 if success else -0.35), 2)
            return {"production": production_shift, "morale": 3 if success else -2, "timeline_updates": 1}

        if inputs.decision_type == "espionage":
            intel_yield = int((20 + monte_carlo["successes"]) * factors.get("intelligence_index", 0.5))
            casualties = 1 if success else max(2, int(4 * (1 - factors.get("fog_of_war", 0.5))))
            return {
                "intelligence_gained": intel_yield if success else max(0, intel_yield // 4),
                "casualties": casualties,
                "morale": 1 if success else -2,
            }

        if inputs.decision_type == "military_action":
            forces = float(inputs.decision_data.get("forces", 5000))
            base_casualty_rate = 0.06 + (1 - probability) * 0.20
            weather_penalty = max(0, 0.5 - factors.get("weather_modifier", 0.5)) * 0.10
            fatigue_penalty = max(0, 0.5 - factors.get("fatigue_modifier", 0.5)) * 0.08
            casualty_rate = base_casualty_rate + weather_penalty + fatigue_penalty
            casualties = int(forces * casualty_rate)
            territory = 1 if success else 0
            if success and probability > 0.75:
                territory = 2  # Decisive victory gains extra territory
            morale_impact = (8 + int(probability * 5)) if success else -(5 + int((1 - probability) * 5))
            return {
                "territory_gained": territory,
                "casualties": casualties,
                "morale_impact": morale_impact,
                "supply_strain": round(max(0, forces / coalition_resource_total * 100), 2),
            }

        # Diplomacy
        diplomatic_gain = int(150 + coalition_resource_total * 0.00002)
        alliance_change = 5 if success else -3
        return {
            "alliance_strength": alliance_change,
            "resources_gained": diplomatic_gain if success else 0,
            "morale": 2 if success else -1,
            "timeline_updates": 1 if success else 0,
        }

    # ── Counterfactual Divergence ─────────────────────────────────────────

    def _calculate_divergence(self, inputs: SimulationInputs, success: bool, probability: float) -> dict:
        year = inputs.baseline.get("year", 1942)
        side = inputs.baseline.get("side", "allies")
        historical = HISTORICAL_OUTCOMES.get(inputs.decision_type, {}).get(side, {})

        hist_success_rate = 0.5
        for (y_start, y_end), data in historical.items():
            if y_start <= year <= y_end:
                hist_success_rate = data.get("success_rate", 0.5)
                break

        expected_success = probability >= 0.5
        actual_matches_history = (success == (hist_success_rate >= 0.5))
        divergence = abs(probability - hist_success_rate)

        if not actual_matches_history:
            divergence *= 1.5  # Divergent outcomes amplify the score

        return {
            "historical_baseline": round(hist_success_rate, 4),
            "simulation_probability": round(probability, 4),
            "divergence_score": round(divergence, 4),
            "matches_history": actual_matches_history,
            "scenario_year": year,
            "interpretation": self._divergence_interpretation(divergence, actual_matches_history),
        }

    def _divergence_interpretation(self, divergence: float, matches: bool) -> str:
        if divergence < 0.10:
            return "Closely follows historical trajectory."
        if divergence < 0.25:
            return "Minor deviation from historical patterns." if matches else "Moderate counterfactual divergence — alternative history emerging."
        if divergence < 0.45:
            return "Significant divergence from historical record." if matches else "Major counterfactual shift — timeline substantially altered."
        return "Extreme divergence — this timeline bears little resemblance to actual history."

    # ── Follow-up Scenario Generation ─────────────────────────────────────

    def _generate_follow_up_scenarios(self, inputs: SimulationInputs, success: bool, impact: dict, rng: random.Random) -> list[dict]:
        scenarios = []
        if inputs.decision_type == "military_action":
            if success:
                scenarios.append({
                    "type": "military_action",
                    "name": "Exploitation Advance",
                    "description": "Press the advantage with a follow-up offensive to exploit the breach.",
                    "risk": "medium",
                    "recommended_forces": int(float(inputs.decision_data.get("forces", 5000)) * 0.7),
                })
                scenarios.append({
                    "type": "resource_allocation",
                    "name": "Consolidate Position",
                    "description": "Reinforce the captured territory and establish supply lines.",
                    "risk": "low",
                    "recommended_amount": 5000,
                })
            else:
                scenarios.append({
                    "type": "diplomacy",
                    "name": "Request Allied Reinforcements",
                    "description": "Seek additional coalition support to prepare for another attempt.",
                    "risk": "low",
                })
                scenarios.append({
                    "type": "espionage",
                    "name": "Reconnaissance in Force",
                    "description": "Gather better intelligence before committing to another assault.",
                    "risk": "medium",
                })
        elif inputs.decision_type == "espionage":
            if success:
                scenarios.append({
                    "type": "military_action",
                    "name": "Intelligence-Led Strike",
                    "description": "Use the gathered intelligence for a precision military operation.",
                    "risk": "medium",
                    "recommended_forces": 8000,
                })
            else:
                scenarios.append({
                    "type": "diplomacy",
                    "name": "Diplomatic Cover",
                    "description": "Use diplomatic channels to extract compromised operatives.",
                    "risk": "low",
                })
        elif inputs.decision_type == "resource_allocation":
            scenarios.append({
                "type": "military_action",
                "name": "Resource-Backed Offensive",
                "description": "Launch an offensive backed by newly allocated resources.",
                "risk": "medium",
                "recommended_forces": 10000,
            })
        elif inputs.decision_type == "diplomacy":
            if success:
                scenarios.append({
                    "type": "resource_allocation",
                    "name": "Allied Resource Integration",
                    "description": "Integrate newly secured allied resources into the war effort.",
                    "risk": "low",
                    "recommended_amount": impact.get("resources_gained", 500),
                })
        # Always offer a strategic option based on overall context
        year = inputs.baseline.get("year", 1942)
        if year >= 1944:
            scenarios.append({
                "type": "military_action",
                "name": "Final Offensive",
                "description": f"With the war entering its final phase ({year}), consider a decisive campaign.",
                "risk": "high",
                "recommended_forces": 20000,
            })
        return scenarios[:3]  # Return top 3 scenarios

    # ── Narrative generation ──────────────────────────────────────────────

    def _generate_narrative(self, inputs: SimulationInputs, success: bool, probability: float, factors: dict, impact: dict) -> str:
        templates = NARRATIVES.get(inputs.decision_type, NARRATIVES["military_action"])
        template_list = templates.get(success, templates[True])
        rng = random.Random(f"{inputs.seed}:narrative:{inputs.turn_number}")
        template = rng.choice(template_list)

        location = inputs.decision_data.get("location", "the front")
        target = inputs.decision_data.get("target", inputs.decision_data.get("target_nation", "the enemy"))
        resource = inputs.decision_data.get("resource", "strategic materials")

        try:
            return template.format(
                location=location,
                target=target,
                resource=resource,
                casualties=impact.get("casualties", 0),
                territory_gained=impact.get("territory_gained", 0),
                morale_impact=abs(impact.get("morale_impact", impact.get("morale", 0))),
                probability=probability,
                historical=inputs.baseline.get("historical_success_rate", 0.5),
                leadership=factors.get("leadership_index", 0.5),
                supply=factors.get("supply_chain", 0.5),
                weather_desc=self._weather_description(factors.get("weather_modifier", 0.5)),
                fatigue=factors.get("fatigue_modifier", 0.5),
                fog=factors.get("fog_of_war", 0.5),
                intelligence_gained=impact.get("intelligence_gained", 0),
                production=impact.get("production", 0),
                resource_index=factors.get("resource_index", 0.5),
                alliance_strength=abs(impact.get("alliance_strength", 0)),
                resources_gained=impact.get("resources_gained", 0),
                alignment=factors.get("target_alignment", 0.5),
                source_type=inputs.decision_data.get("source_type", "covert operations"),
            )
        except (KeyError, IndexError):
            verdict = "succeeded" if success else "failed"
            return f"{inputs.decision_type.replace('_', ' ').title()} {verdict} with {probability:.0%} probability."

    def _weather_description(self, factor: float) -> str:
        if factor >= 0.6:
            return "favourable"
        if factor >= 0.45:
            return "moderate"
        if factor >= 0.3:
            return "challenging"
        return "severely adverse"

    # ── Utility ───────────────────────────────────────────────────────────

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))
