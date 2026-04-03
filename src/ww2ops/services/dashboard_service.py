from src.ww2ops.db.models import Battle, Campaign, GeographicRegion, IntelligenceReport, Leader, Nation, Operation, ResourceSnapshot, WarEvent


class DashboardService:
    def get_resource_overview(self):
        snapshots = (
            ResourceSnapshot.query.filter(ResourceSnapshot.simulation_id.is_(None))
            .order_by(ResourceSnapshot.nation_id.asc(), ResourceSnapshot.snapshot_date.desc())
            .all()
        )
        latest_by_nation = {}
        for snapshot in snapshots:
            if snapshot.nation and snapshot.nation.name not in latest_by_nation:
                latest_by_nation[snapshot.nation.name] = snapshot

        ranked = sorted(
            latest_by_nation.items(),
            key=lambda item: (
                float((item[1].metrics or {}).get('cinc') or 0),
                sum(float(balance.amount) for balance in item[1].balances),
                item[0],
            ),
            reverse=True,
        )

        payload = {}
        for nation_name, snapshot in ranked[:12]:
            balances = {balance.resource_type.code: float(balance.amount) for balance in snapshot.balances if balance.resource_type}
            metrics = snapshot.metrics or {}
            payload[nation_name] = {
                'oil': balances.get('oil', 0),
                'steel': balances.get('steel', 0),
                'manpower': balances.get('manpower', 0),
                'food': balances.get('food', 0),
                'ammunition': balances.get('ammunition', 0),
                'aircraft': balances.get('aircraft', 0),
                'naval_tonnage': balances.get('naval_tonnage', 0),
                'rubber': balances.get('rubber', 0),
                'gdp': metrics.get('gdp', 0),
                'morale': metrics.get('morale', 0),
                'cinc': metrics.get('cinc', 0),
                'territory_count': metrics.get('territory_count', 0),
                'snapshot_date': snapshot.snapshot_date.isoformat(),
                'side': snapshot.nation.side,
                'alliance': snapshot.nation.alliance.name if snapshot.nation.alliance else None,
            }
        return payload

    def get_territory_overview(self):
        regions = GeographicRegion.query.filter(GeographicRegion.latitude.is_not(None)).all()
        return [
            {
                'id': region.id,
                'name': region.name,
                'lat': region.latitude,
                'lng': region.longitude,
                'controlled_by': (region.metadata_json or {}).get('controlled_by', 'Contested'),
                'strategic_value': region.strategic_rating or 0,
                'theater': region.theater,
                'parent': region.parent_region.name if region.parent_region else None,
            }
            for region in regions
        ]

    def get_recent_intelligence(self):
        reports = IntelligenceReport.query.order_by(IntelligenceReport.report_date.desc()).limit(20).all()
        return [
            {
                'id': report.id,
                'date': report.report_date.isoformat(),
                'classification': report.classification or 'secret',
                'source': report.source_type or 'archival',
                'report_type': report.report_type,
                'content': report.content,
                'decoded': report.decoded,
                'confidence': report.confidence_level,
                'side': report.nation.side if report.nation else 'unknown',
                'nation': report.nation.name if report.nation else None,
                'location': report.region.name if report.region else None,
                'source_reference': report.source_reference,
            }
            for report in reports
        ]

    def get_battles(self):
        battles = Battle.query.order_by(Battle.start_date.asc()).all()
        return [
            {
                'id': battle.id,
                'name': battle.name,
                'start_date': battle.start_date.isoformat() if battle.start_date else None,
                'end_date': battle.end_date.isoformat() if battle.end_date else None,
                'location': battle.location_name,
                'lat': battle.latitude,
                'lng': battle.longitude,
                'victor': battle.victor_side,
                'axis_forces': battle.axis_forces or 0,
                'allied_forces': battle.allied_forces or 0,
                'axis_casualties': battle.axis_casualties or 0,
                'allied_casualties': battle.allied_casualties or 0,
                'total_casualties': (battle.axis_casualties or 0) + (battle.allied_casualties or 0),
                'description': battle.description,
                'campaign': battle.campaign.name if battle.campaign else None,
                'theater': battle.region.theater if battle.region else None,
            }
            for battle in battles
        ]

    def get_stats(self):
        first_event = WarEvent.query.order_by(WarEvent.event_date.asc()).first()
        last_event = WarEvent.query.order_by(WarEvent.event_date.desc()).first()

        # Count by side
        allied_nations = Nation.query.filter_by(side='allies').count()
        axis_nations = Nation.query.filter_by(side='axis').count()

        return {
            'total_battles': Battle.query.count(),
            'total_operations': Operation.query.count(),
            'total_campaigns': Campaign.query.count(),
            'total_territories': GeographicRegion.query.count(),
            'total_intelligence_reports': IntelligenceReport.query.count(),
            'total_leaders': Leader.query.count(),
            'total_war_events': WarEvent.query.count(),
            'coalition_breakdown': {
                'allied_nations': allied_nations,
                'axis_nations': axis_nations,
            },
            'date_range': {
                'start': first_event.event_date.date().isoformat() if first_event else None,
                'end': last_event.event_date.date().isoformat() if last_event else None,
            },
        }

    def get_force_composition(self):
        """Detailed military force breakdown by nation and resource type."""
        nations = Nation.query.all()
        composition = []
        for nation in nations:
            snapshot = (
                ResourceSnapshot.query.filter(
                    ResourceSnapshot.nation_id == nation.id,
                    ResourceSnapshot.simulation_id.is_(None),
                )
                .order_by(ResourceSnapshot.snapshot_date.desc())
                .first()
            )
            if not snapshot:
                continue
            balances = {b.resource_type.code: float(b.amount) for b in snapshot.balances if b.resource_type}
            metrics = snapshot.metrics or {}
            composition.append({
                'nation': nation.name,
                'side': nation.side,
                'manpower': balances.get('manpower', 0),
                'aircraft': balances.get('aircraft', 0),
                'naval_tonnage': balances.get('naval_tonnage', 0),
                'oil': balances.get('oil', 0),
                'steel': balances.get('steel', 0),
                'morale': metrics.get('morale', 0),
                'cinc': metrics.get('cinc', 0),
            })
        composition.sort(key=lambda x: x.get('cinc', 0), reverse=True)
        return composition
