from datetime import datetime

from src.ww2ops.db.models import GeographicRegion, TimelineEntry, WarEvent


class TimelineService:
    def list_events(self, start_year: int, end_year: int, simulation_id: int | None = None, theater: str | None = None, event_type: str | None = None):
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        events = []

        # Historical war events
        query = WarEvent.query.filter(WarEvent.event_date >= start, WarEvent.event_date <= end)
        if theater:
            query = query.filter(WarEvent.region.has(GeographicRegion.theater == theater))
        if event_type:
            query = query.filter(WarEvent.event_type == event_type)

        historical_events = query.order_by(WarEvent.event_date.asc(), WarEvent.id.asc()).all()

        for event in historical_events:
            description = event.summary
            if not description and event.battle:
                description = event.battle.description
            if not description and event.operation:
                description = event.operation.description
            item = {
                'type': event.event_type,
                'id': event.id,
                'name': event.name,
                'date': event.event_date.isoformat(),
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'location': event.battle.location_name if event.battle and event.battle.location_name else event.region.name if event.region else None,
                'theater': event.region.theater if event.region else None,
                'description': description,
                'confidence': event.confidence_level,
            }
            if event.battle:
                item['victor'] = event.battle.victor_side
                item['axis_casualties'] = event.battle.axis_casualties or 0
                item['allied_casualties'] = event.battle.allied_casualties or 0
                item['total_casualties'] = (event.battle.axis_casualties or 0) + (event.battle.allied_casualties or 0)
                item['axis_forces'] = event.battle.axis_forces or 0
                item['allied_forces'] = event.battle.allied_forces or 0
                item['lat'] = event.battle.latitude
                item['lng'] = event.battle.longitude
            if event.operation:
                item['code_name'] = event.operation.code_name
                item['side'] = event.operation.side
                item['outcome'] = event.operation.outcome
                item['objective'] = event.operation.objective
            events.append(item)

        # Simulation timeline entries
        simulation_query = TimelineEntry.query.filter(TimelineEntry.entry_date >= start, TimelineEntry.entry_date <= end)
        if simulation_id is not None:
            simulation_query = simulation_query.filter_by(simulation_id=simulation_id)
        simulation_entries = simulation_query.order_by(TimelineEntry.entry_date.asc(), TimelineEntry.id.asc()).all()
        region_ids = sorted({entry.region_id for entry in simulation_entries if entry.region_id is not None})
        region_lookup = {}
        if region_ids:
            region_lookup = {region.id: region for region in GeographicRegion.query.filter(GeographicRegion.id.in_(region_ids)).all()}

        for entry in simulation_entries:
            payload = entry.payload or {}
            region = region_lookup.get(entry.region_id)
            item = {
                'type': entry.entry_type,
                'id': entry.id,
                'name': entry.headline,
                'date': entry.entry_date.isoformat(),
                'location': (region.name if region else None) or payload.get('location'),
                'theater': (region.theater if region else None) or payload.get('theater'),
                'description': entry.summary,
                'simulation_id': entry.simulation_id,
            }
            if payload.get('success') is True:
                item['outcome'] = 'success'
            elif payload.get('success') is False:
                item['outcome'] = 'failure'
            events.append(item)

        events.sort(key=lambda item: item['date'])
        return events

    def get_available_filters(self):
        """Return available filter options for the timeline."""
        theaters = sorted({r.theater for r in GeographicRegion.query.filter(GeographicRegion.theater.is_not(None)).all()})
        event_types = sorted({e.event_type for e in WarEvent.query.with_entities(WarEvent.event_type).distinct().all() if e.event_type})
        return {
            "theaters": theaters,
            "event_types": event_types,
            "year_range": {"start": 1939, "end": 1945},
        }
