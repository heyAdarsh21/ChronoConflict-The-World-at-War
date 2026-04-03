from datetime import datetime

from sqlalchemy import func

from src.ww2ops.db.models import WarCrime, WarEvent


class AftermathService:
    def list_events(self, category=None, start_year=None, end_year=None, region=None):
        query = WarCrime.query.join(WarCrime.war_event)
        if category:
            query = query.filter(WarCrime.category == category)
        if region:
            query = query.filter(WarCrime.war_event.has(WarEvent.region.has(name=region)))
        if start_year:
            query = query.filter(WarCrime.war_event.has(WarEvent.event_date >= datetime(start_year, 1, 1)))
        if end_year:
            query = query.filter(WarCrime.war_event.has(WarEvent.event_date <= datetime(end_year, 12, 31)))
        events = query.order_by(WarCrime.id.asc()).all()
        categories = [row[0] for row in WarCrime.query.with_entities(WarCrime.category).distinct().all()]
        regions = sorted({
            event.war_event.region.name
            for event in events
            if event.war_event and event.war_event.region
        })

        # Aggregation statistics
        total_death_toll = sum(event.death_toll or 0 for event in events)
        by_category = {}
        for event in events:
            cat = event.category or "unknown"
            if cat not in by_category:
                by_category[cat] = {"count": 0, "total_deaths": 0}
            by_category[cat]["count"] += 1
            by_category[cat]["total_deaths"] += event.death_toll or 0

        return {
            "events": [
                {
                    "id": event.id,
                    "title": event.war_event.name,
                    "event_date": event.war_event.event_date.isoformat() if event.war_event.event_date else None,
                    "end_date": event.war_event.end_date.isoformat() if event.war_event.end_date else None,
                    "location": event.location_name,
                    "region": event.war_event.region.name if event.war_event.region else None,
                    "perpetrators": event.perpetrators,
                    "victims": event.victims,
                    "death_toll": event.death_toll,
                    "category": event.category,
                    "description": event.description,
                    "sources": event.sources,
                    "media_url": event.media_url,
                    "sensitivity_notes": event.sensitivity_notes,
                }
                for event in events
            ],
            "categories": sorted([item for item in categories if item]),
            "regions": regions,
            "aggregation": {
                "total_events": len(events),
                "total_death_toll": total_death_toll,
                "by_category": by_category,
            },
        }
