from __future__ import annotations

import random
from datetime import datetime

from src.ww2ops.db.models import IntelligenceReport, Nation, Operation, ResourceBalance, ResourceSnapshot, ResourceType, Simulation, SimulationAuditEvent, SimulationDecision, SimulationOutcome, TimelineEntry
from src.ww2ops.extensions import db
from src.ww2ops.repositories.simulation_repository import SimulationRepository
from src.ww2ops.services.simulation_engine import SimulationContext, SimulationEngine, SimulationInputs


class SimulationService:
    def __init__(self):
        self.engine = SimulationEngine()

    def start_simulation(self, user_id: int, scenario_name: str, start_year: int, side: str, seed: int | None = None):
        simulation = Simulation(
            user_id=user_id,
            scenario_name=scenario_name,
            start_year=start_year,
            side=side,
            seed=seed or random.randint(1, 2147483647),
            parameters={"scenario_name": scenario_name, "start_year": start_year, "side": side},
        )
        db.session.add(simulation)
        db.session.commit()
        return simulation

    def get_simulation_for_user(self, simulation_id: int, user_id: int):
        simulation = SimulationRepository.get_for_user(simulation_id, user_id)
        if not simulation:
            raise LookupError('Simulation not found')
        return simulation

    def process_decision(self, simulation: Simulation, decision_type: str, decision_data: dict):
        turn_number = simulation.current_turn + 1
        decision = SimulationDecision(
            simulation_id=simulation.id,
            turn_number=turn_number,
            decision_type=decision_type,
            payload=decision_data,
        )
        db.session.add(decision)
        db.session.flush()

        baseline = self._build_baseline(simulation, decision_type, decision_data, turn_number)
        result = self.engine.evaluate(
            SimulationInputs(
                seed=simulation.seed,
                turn_number=turn_number,
                decision_type=decision_type,
                decision_data=decision_data,
                baseline=baseline,
            )
        )
        snapshot_date = datetime(min(max(simulation.start_year, 1939), 1945), min(turn_number, 12), 1)
        self._apply_simulation_impacts(simulation, decision_type, decision_data, result, snapshot_date)
        self._record_simulation_intelligence(simulation, decision_type, decision_data, result, snapshot_date)

        db.session.add(
            SimulationOutcome(
                simulation_id=simulation.id,
                decision_id=decision.id,
                success_probability=result['probability'],
                realized_success=result['success'],
                weighted_score=result['weighted_score'],
                narrative_summary=result['message'],
                impact_payload=result,
            )
        )
        db.session.add(
            SimulationAuditEvent(
                simulation_id=simulation.id,
                decision_id=decision.id,
                event_type='decision_processed',
                detail={'baseline': baseline, 'result': result},
            )
        )
        db.session.add(
            TimelineEntry(
                simulation_id=simulation.id,
                entry_type=f"simulation_{decision_type}",
                headline=f"{simulation.scenario_name}: {decision_type.replace('_', ' ').title()}",
                summary=result['message'],
                entry_date=snapshot_date,
                payload=result,
            )
        )

        simulation.current_turn = turn_number
        simulation.latest_outcome = result
        db.session.commit()
        return decision, result

    def _build_baseline(self, simulation: Simulation, decision_type: str, decision_data: dict, turn_number: int):
        scenario_year = min(max(simulation.start_year + turn_number - 1, 1939), 1945)
        coalition_nations = Nation.query.filter_by(side=simulation.side).all()
        coalition_ids = [nation.id for nation in coalition_nations]
        snapshots = []
        for nation in coalition_nations:
            snapshot = (
                ResourceSnapshot.query.filter(
                    ResourceSnapshot.nation_id == nation.id,
                    ResourceSnapshot.simulation_id.is_(None),
                    ResourceSnapshot.snapshot_date <= datetime(scenario_year, 12, 31),
                )
                .order_by(ResourceSnapshot.snapshot_date.desc())
                .first()
            )
            if snapshot:
                snapshots.append(snapshot)

        resource_total = 0.0
        coalition_cinc = 0.0
        morale_values = []
        for snapshot in snapshots:
            balances = {balance.resource_type.code: float(balance.amount) for balance in snapshot.balances}
            resource_total += balances.get('oil', 0) + balances.get('steel', 0) + balances.get('manpower', 0)
            coalition_cinc += float((snapshot.metrics or {}).get('cinc') or 0)
            if (snapshot.metrics or {}).get('morale') is not None:
                morale_values.append(float(snapshot.metrics.get('morale')))

        all_snapshots_same_year = ResourceSnapshot.query.filter(
            ResourceSnapshot.simulation_id.is_(None),
            ResourceSnapshot.snapshot_date <= datetime(scenario_year, 12, 31),
        ).all()
        max_resource_total = max([sum(float(balance.amount) for balance in snap.balances) for snap in all_snapshots_same_year] or [1.0])
        resource_index = min(1.0, resource_total / max_resource_total) if max_resource_total else 0.5
        leaders = [leader for nation in coalition_nations for leader in nation.leaders]
        leadership_index = min(1.0, (sum((leader.influence_score or 60) for leader in leaders) / max(len(leaders), 1)) / 100)
        reports = IntelligenceReport.query.filter(IntelligenceReport.nation_id.in_(coalition_ids)).all() if coalition_ids else []
        intelligence_index = min(
            1.0,
            (sum((report.confidence_level or 0.5) + (0.15 if report.decoded else 0) for report in reports) / max(len(reports), 1)),
        ) if reports else 0.45
        morale = min(1.0, ((sum(morale_values) / max(len(morale_values), 1)) / 100) if morale_values else 0.55)
        historical_success_rate = self._historical_success_rate(simulation.side, decision_type, decision_data, scenario_year)
        target_alignment = self._target_alignment(simulation.side, decision_type, decision_data)
        theater_advantage = self._theater_advantage(simulation.side, decision_data)
        coalition_depth = min(1.0, len(coalition_nations) / 8) if coalition_nations else 0.2
        return {
            'resource_index': resource_index,
            'leadership_index': leadership_index,
            'intelligence_index': intelligence_index,
            'morale': morale,
            'historical_success_rate': historical_success_rate,
            'target_alignment': target_alignment,
            'theater_advantage': theater_advantage,
            'coalition_depth': coalition_depth,
            'resource_total': resource_total,
            'coalition_cinc': coalition_cinc,
            'year': scenario_year,
        }

    def _historical_success_rate(self, side: str, decision_type: str, decision_data: dict, scenario_year: int):
        query = Operation.query.filter(Operation.start_date <= datetime(scenario_year, 12, 31))
        if decision_type == 'military_action':
            query = query.filter_by(side=side)
            location = (decision_data.get('location') or '').lower()
            if location:
                query = query.filter(Operation.description.ilike(f"%{location}%") | Operation.name.ilike(f"%{location}%"))
        elif decision_type == 'diplomacy':
            return 0.72 if self._target_alignment(side, decision_type, decision_data) > 0.75 else 0.38
        elif decision_type == 'espionage':
            reports = IntelligenceReport.query.filter(IntelligenceReport.nation.has(side=side)).all()
            decoded = sum(1 for report in reports if report.decoded)
            return decoded / max(len(reports), 1) if reports else 0.42
        else:
            query = query.filter_by(side=side)

        operations = query.all()
        if not operations:
            return 0.5
        successes = sum(1 for operation in operations if (operation.outcome or '').lower() == 'success')
        return successes / len(operations)

    def _target_alignment(self, side: str, decision_type: str, decision_data: dict):
        target_name = decision_data.get('target_nation') or decision_data.get('target')
        if not target_name:
            return 0.5
        target = Nation.query.filter((Nation.name == target_name) | (Nation.code == target_name)).first()
        if target is None or not target.side:
            return 0.5
        if decision_type == 'espionage':
            return 0.3 if target.side != side else 0.85
        return 0.92 if target.side == side else 0.25

    def _theater_advantage(self, side: str, decision_data: dict):
        location = (decision_data.get('location') or '').lower()
        if not location:
            return 0.5
        matching_ops = Operation.query.filter(Operation.description.ilike(f"%{location}%") | Operation.name.ilike(f"%{location}%")).all()
        if not matching_ops:
            return 0.5
        favorable = sum(1 for operation in matching_ops if operation.side == side and (operation.outcome or '').lower() == 'success')
        return favorable / len(matching_ops)

    def _apply_simulation_impacts(self, simulation: Simulation, decision_type: str, decision_data: dict, result: dict, snapshot_date: datetime):
        coalition_nations = Nation.query.filter_by(side=simulation.side).all()
        if not coalition_nations:
            return
        base_snapshots = []
        for nation in coalition_nations:
            latest = (
                ResourceSnapshot.query.filter_by(nation_id=nation.id, simulation_id=simulation.id)
                .order_by(ResourceSnapshot.snapshot_date.desc())
                .first()
            )
            if latest is None:
                latest = (
                    ResourceSnapshot.query.filter(
                        ResourceSnapshot.nation_id == nation.id,
                        ResourceSnapshot.simulation_id.is_(None),
                    )
                    .order_by(ResourceSnapshot.snapshot_date.desc())
                    .first()
                )
            if latest is not None:
                base_snapshots.append((nation, latest))

        total_cinc = sum(float((snapshot.metrics or {}).get('cinc') or 0) for _, snapshot in base_snapshots) or len(base_snapshots)
        for nation, base_snapshot in base_snapshots:
            share = (float((base_snapshot.metrics or {}).get('cinc') or 1) / total_cinc) if total_cinc else 1 / len(base_snapshots)
            balances = {balance.resource_type.code: float(balance.amount) for balance in base_snapshot.balances}
            metrics = dict(base_snapshot.metrics or {})
            if decision_type == 'resource_allocation':
                target_resource = decision_data.get('resource') or 'steel'
                balances[target_resource] = balances.get(target_resource, 0) - float(decision_data.get('amount', 0)) * share
                balances['steel'] = balances.get('steel', 0) + float(result.get('production', 0)) * share
            elif decision_type == 'military_action':
                balances['manpower'] = max(0, balances.get('manpower', 0) - float(result.get('casualties', 0)) * share)
                metrics['territory_count'] = float(metrics.get('territory_count') or 1) + float(result.get('territory_gained', 0)) * share
            elif decision_type == 'diplomacy':
                balances['oil'] = balances.get('oil', 0) + float(result.get('resources_gained', 0)) * share
                balances['steel'] = balances.get('steel', 0) + float(result.get('resources_gained', 0)) * 0.5 * share
            metrics['morale'] = max(0, min(100, float(metrics.get('morale') or 50) + float(result.get('morale', result.get('morale_impact', 0))) * share))
            self._upsert_simulation_snapshot(
                simulation.id,
                nation.id,
                snapshot_date,
                balances,
                metrics,
                base_snapshot.source or 'simulation',
                base_snapshot.confidence_level or 0.8,
            )

    def _upsert_simulation_snapshot(self, simulation_id: int, nation_id: int, snapshot_date: datetime, balances: dict, metrics: dict, source: str, confidence: float):
        snapshot = ResourceSnapshot.query.filter_by(simulation_id=simulation_id, nation_id=nation_id, snapshot_date=snapshot_date).first()
        if snapshot is None:
            snapshot = ResourceSnapshot(simulation_id=simulation_id, nation_id=nation_id, snapshot_date=snapshot_date)
            db.session.add(snapshot)
            db.session.flush()

        snapshot.source = source
        snapshot.confidence_level = confidence
        snapshot.metrics = metrics

        existing = {balance.resource_type.code: balance for balance in ResourceBalance.query.filter_by(snapshot_id=snapshot.id).all()}
        for resource_type in ResourceType.query.order_by(ResourceType.code.asc()).all():
            balance = existing.get(resource_type.code)
            if balance is None:
                balance = ResourceBalance(snapshot_id=snapshot.id, resource_type_id=resource_type.id, amount=0)
                db.session.add(balance)
            balance.amount = float(balances.get(resource_type.code, balance.amount or 0))

        db.session.flush()

    def _record_simulation_intelligence(self, simulation: Simulation, decision_type: str, decision_data: dict, result: dict, snapshot_date: datetime):
        if decision_type != 'espionage':
            return
        target_name = decision_data.get('target') or 'Unknown'
        target = Nation.query.filter((Nation.name == target_name) | (Nation.code == target_name)).first()
        report = IntelligenceReport(
            simulation_id=simulation.id,
            nation_id=target.id if target else None,
            report_date=snapshot_date,
            classification='secret',
            source_type='simulation_espionage',
            report_type='field_intelligence',
            content=result['message'],
            decoded=result.get('success', False),
            confidence_level=result.get('probability', 0.5),
            source_reference=f"simulation:{simulation.id}:turn:{simulation.current_turn + 1}",
        )
        db.session.add(report)
