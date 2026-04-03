"""Comprehensive seed service that populates the database with rich, interconnected WWII data.

Uses dedicated data modules for leaders, battles, operations, and resources to ensure
the database is always richly populated without depending on external APIs.
"""

from __future__ import annotations

from datetime import date, datetime

from src.ww2ops.db.models import (
    Alliance,
    Battle,
    Campaign,
    CommandAssignment,
    GeographicRegion,
    IntelligenceReport,
    Leader,
    Nation,
    Operation,
    ResourceBalance,
    ResourceSnapshot,
    ResourceType,
    TimelineEntry,
    WarCrime,
    WarEvent,
)
from src.ww2ops.extensions import db
from src.ww2ops.services.seed_data_battles import BATTLES
from src.ww2ops.services.seed_data_leaders import LEADERS
from src.ww2ops.services.seed_data_operations import (
    CAMPAIGNS,
    INTELLIGENCE_REPORTS,
    OPERATIONS,
    WAR_CRIMES,
    WAR_EVENTS,
)
from src.ww2ops.services.seed_data_resources import (
    GEOGRAPHIC_REGIONS,
    NATIONS,
    RESOURCE_SNAPSHOTS,
    RESOURCE_TYPES,
)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


class SeedService:
    """Seeds the database with a comprehensive, self-contained WWII dataset."""

    def seed_if_empty(self):
        if Nation.query.count():
            return
        self.seed_reference_data()

    def seed_reference_data(self):
        """Full seed pipeline — alliances, nations, regions, resource types, leaders,
        campaigns, battles, operations, resources, intelligence, war events, war crimes,
        and timeline entries."""
        alliances = self._seed_alliances()
        regions = self._seed_regions()
        nations = self._seed_nations(alliances)
        resource_types = self._seed_resource_types()
        self._seed_leaders(nations)
        campaigns = self._seed_campaigns(regions)
        battles = self._seed_battles(campaigns, regions)
        operations = self._seed_operations(campaigns, regions)
        self._seed_command_assignments(nations, operations, campaigns)
        self._seed_resource_snapshots(nations, resource_types)
        self._seed_intelligence_reports(nations, regions)
        war_events = self._seed_war_events(regions, battles, operations)
        self._seed_war_crimes(war_events)
        self._seed_timeline_entries(war_events, regions)
        db.session.commit()

    # ── Alliances ──────────────────────────────────────────────────────────

    def _seed_alliances(self) -> dict[str, Alliance]:
        data = [
            ("ALLIES", "Allies", "allies", "The Allied coalition of nations opposing the Axis powers."),
            ("AXIS", "Axis", "axis", "The Axis coalition led by Germany, Italy, and Japan."),
            ("NEUTRAL", "Neutral", "neutral", "States outside the principal wartime coalitions."),
        ]
        alliances = {}
        for code, name, side, description in data:
            alliance = Alliance(name=name, code=code, side=side, description=description, doctrine={"source": "curated"})
            db.session.add(alliance)
            alliances[code] = alliance
        db.session.flush()
        return alliances

    # ── Geographic Regions ─────────────────────────────────────────────────

    def _seed_regions(self) -> dict[str, GeographicRegion]:
        regions: dict[str, GeographicRegion] = {}
        # First pass: create all regions without parents
        for item in GEOGRAPHIC_REGIONS:
            region = GeographicRegion(
                name=item["name"],
                theater=item.get("theater"),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                strategic_rating=item.get("strategic_rating"),
            )
            db.session.add(region)
            regions[item["name"]] = region
        db.session.flush()
        # Second pass: link parents
        for item in GEOGRAPHIC_REGIONS:
            parent_name = item.get("parent")
            if parent_name and parent_name in regions:
                regions[item["name"]].parent_region_id = regions[parent_name].id
        db.session.flush()
        return regions

    # ── Nations ────────────────────────────────────────────────────────────

    def _seed_nations(self, alliances: dict[str, Alliance]) -> dict[str, Nation]:
        nations = {}
        for item in NATIONS:
            nation = Nation(
                name=item["name"],
                code=item["code"],
                side=item.get("side"),
                alliance_id=alliances.get(item.get("alliance", ""), alliances.get("NEUTRAL")).id,
                capital=item.get("capital"),
                ideology=item.get("ideology"),
                description=item.get("description"),
            )
            db.session.add(nation)
            nations[item["name"]] = nation
        db.session.flush()
        return nations

    # ── Resource Types ─────────────────────────────────────────────────────

    def _seed_resource_types(self) -> dict[str, ResourceType]:
        resource_types = {}
        for code, name, unit, category in RESOURCE_TYPES:
            rt = ResourceType(code=code, name=name, unit=unit, category=category)
            db.session.add(rt)
            resource_types[code] = rt
        db.session.flush()
        return resource_types

    # ── Leaders ────────────────────────────────────────────────────────────

    def _seed_leaders(self, nations: dict[str, Nation]):
        for item in LEADERS:
            nation = nations.get(item["country"])
            if not nation:
                continue
            leader = Leader(
                nation_id=nation.id,
                name=item["name"],
                title=item.get("title"),
                role_type=item.get("role_type"),
                biography=item.get("biography"),
                ideology=item.get("ideology"),
                influence_score=item.get("influence_score"),
                born_on=_parse_date(item.get("born_on")),
                died_on=_parse_date(item.get("died_on")),
                notable_quotes=item.get("notable_quotes"),
                metadata_json={"key_operations": item.get("key_operations", [])},
            )
            db.session.add(leader)
        db.session.flush()

    # ── Campaigns ──────────────────────────────────────────────────────────

    def _seed_campaigns(self, regions: dict[str, GeographicRegion]) -> dict[str, Campaign]:
        campaigns = {}
        for item in CAMPAIGNS:
            region = regions.get(item.get("region"))
            campaign = Campaign(
                name=item["name"],
                theater=item.get("theater"),
                region_id=region.id if region else None,
                start_date=_parse_dt(item.get("start_date")),
                end_date=_parse_dt(item.get("end_date")),
                description=item.get("description"),
                outcome=item.get("outcome"),
                strategic_value=item.get("strategic_value"),
            )
            db.session.add(campaign)
            campaigns[item["name"]] = campaign
        db.session.flush()
        return campaigns

    # ── Battles ────────────────────────────────────────────────────────────

    def _seed_battles(self, campaigns: dict[str, Campaign], regions: dict[str, GeographicRegion]) -> dict[str, Battle]:
        battles = {}
        for item in BATTLES:
            campaign = campaigns.get(item.get("campaign"))
            region = regions.get(item.get("region"))
            battle = Battle(
                campaign_id=campaign.id if campaign else None,
                region_id=region.id if region else None,
                name=item["name"],
                location_name=item.get("location_name"),
                start_date=_parse_dt(item["start_date"]),
                end_date=_parse_dt(item.get("end_date")),
                axis_forces=item.get("axis_forces"),
                allied_forces=item.get("allied_forces"),
                axis_casualties=item.get("axis_casualties"),
                allied_casualties=item.get("allied_casualties"),
                victor_side=item.get("victor_side"),
                description=item.get("description"),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
            )
            db.session.add(battle)
            battles[item["name"]] = battle
        db.session.flush()
        return battles

    # ── Operations ─────────────────────────────────────────────────────────

    def _seed_operations(self, campaigns: dict[str, Campaign], regions: dict[str, GeographicRegion]) -> dict[str, Operation]:
        operations = {}
        for item in OPERATIONS:
            campaign = campaigns.get(item.get("campaign"))
            region = regions.get(item.get("region"))
            operation = Operation(
                campaign_id=campaign.id if campaign else None,
                region_id=region.id if region else None,
                name=item["name"],
                code_name=item.get("code_name"),
                side=item.get("side"),
                objective=item.get("objective"),
                outcome=item.get("outcome"),
                start_date=_parse_dt(item["start_date"]),
                end_date=_parse_dt(item.get("end_date")),
                description=item.get("description"),
                analysis=item.get("analysis"),
                intelligence_notes=item.get("intelligence_notes"),
            )
            db.session.add(operation)
            operations[item["name"]] = operation
        db.session.flush()
        return operations

    # ── Command Assignments ────────────────────────────────────────────────

    def _seed_command_assignments(self, nations: dict[str, Nation], operations: dict[str, Operation], campaigns: dict[str, Campaign]):
        assignment_map = {
            "Dwight D. Eisenhower": [("Operation Overlord", "Supreme Commander"), ("Operation Torch", "Commanding General"), ("Operation Neptune", "Supreme Commander")],
            "Erwin Rommel": [("North African Campaign", "Commander, Afrika Korps")],
            "Georgy Zhukov": [("Operation Bagration", "Coordinator"), ("Eastern Front Offensive", "Deputy Supreme Commander")],
            "Bernard Montgomery": [("Operation Overlord", "Ground Forces Commander"), ("Operation Market Garden", "21st Army Group Commander")],
            "Chester W. Nimitz": [("Pacific Naval Campaign", "Commander in Chief Pacific")],
            "Douglas MacArthur": [("Pacific Island Campaign", "Supreme Commander SWPA"), ("Philippine Liberation", "Supreme Commander SWPA")],
            "George S. Patton": [("Western Front Liberation", "Commander, Third Army")],
            "Omar Bradley": [("Western Front Liberation", "Commander, 12th Army Group")],
            "Karl Dönitz": [("Atlantic Naval Campaign", "Commander, U-boat Fleet")],
            "Albert Kesselring": [("Italian Campaign", "Commander, Army Group C")],
            "Konstantin Rokossovsky": [("Eastern Front Offensive", "Commander, Don Front / Central Front")],
        }
        leaders_by_name = {leader.name: leader for leader in Leader.query.all()}
        for leader_name, entries in assignment_map.items():
            leader = leaders_by_name.get(leader_name)
            if not leader:
                continue
            for context_name, position in entries:
                operation = operations.get(context_name)
                campaign = campaigns.get(context_name)
                if not operation and not campaign:
                    continue
                assignment = CommandAssignment(
                    leader_id=leader.id,
                    operation_id=operation.id if operation else None,
                    campaign_id=campaign.id if campaign else None,
                    position=position,
                    start_date=operation.start_date if operation else (campaign.start_date if campaign else None),
                    end_date=operation.end_date if operation else (campaign.end_date if campaign else None),
                    notes=f"Commanded during {context_name}.",
                )
                db.session.add(assignment)
        db.session.flush()

    # ── Resource Snapshots ─────────────────────────────────────────────────

    def _seed_resource_snapshots(self, nations: dict[str, Nation], resource_types: dict[str, ResourceType]):
        for nation_name, snapshots in RESOURCE_SNAPSHOTS.items():
            nation = nations.get(nation_name)
            if not nation:
                continue
            for entry in snapshots:
                snapshot = ResourceSnapshot(
                    nation_id=nation.id,
                    snapshot_date=datetime(entry["year"], 1, 1),
                    source="curated_seed",
                    confidence_level=0.85,
                    metrics={
                        "gdp": entry.get("gdp"),
                        "morale": entry.get("morale"),
                        "cinc": entry.get("cinc"),
                        "territory_count": entry.get("territory_count"),
                    },
                )
                db.session.add(snapshot)
                db.session.flush()
                for code in resource_types:
                    amount = entry.get(code, 0)
                    if amount is None:
                        amount = 0
                    db.session.add(
                        ResourceBalance(
                            snapshot_id=snapshot.id,
                            resource_type_id=resource_types[code].id,
                            amount=float(amount),
                        )
                    )
        db.session.flush()

    # ── Intelligence Reports ───────────────────────────────────────────────

    def _seed_intelligence_reports(self, nations: dict[str, Nation], regions: dict[str, GeographicRegion]):
        for item in INTELLIGENCE_REPORTS:
            nation = nations.get(item.get("nation"))
            region = regions.get(item.get("region"))
            report = IntelligenceReport(
                nation_id=nation.id if nation else None,
                region_id=region.id if region else None,
                report_date=_parse_dt(item["report_date"]) or datetime(1944, 1, 1),
                classification=item.get("classification"),
                source_type=item.get("source_type"),
                report_type=item.get("report_type"),
                content=item["content"],
                decoded=item.get("decoded", False),
                confidence_level=item.get("confidence_level"),
                source_reference=item.get("source_reference"),
            )
            db.session.add(report)
        db.session.flush()

    # ── War Events ─────────────────────────────────────────────────────────

    def _seed_war_events(self, regions: dict[str, GeographicRegion], battles: dict[str, Battle], operations: dict[str, Operation]) -> dict[str, WarEvent]:
        war_events = {}
        for item in WAR_EVENTS:
            region = regions.get(item.get("region"))
            event = WarEvent(
                event_type=item["event_type"],
                name=item["name"],
                event_date=_parse_dt(item["event_date"]) or datetime(1944, 1, 1),
                end_date=_parse_dt(item.get("end_date")),
                summary=item.get("summary"),
                region_id=region.id if region else None,
                source=item.get("source", "curated_seed"),
                confidence_level=0.92,
            )
            db.session.add(event)
            war_events[item["name"]] = event
        # Also create war events for all battles
        for battle_name, battle in battles.items():
            if battle_name not in war_events:
                event = WarEvent(
                    event_type="battle",
                    name=battle_name,
                    event_date=battle.start_date,
                    end_date=battle.end_date,
                    summary=battle.description,
                    region_id=battle.region_id,
                    battle_id=battle.id,
                    source="curated_seed",
                    confidence_level=0.93,
                )
                db.session.add(event)
                war_events[battle_name] = event
        # Also for operations
        for op_name, operation in operations.items():
            if op_name not in war_events:
                event = WarEvent(
                    event_type="operation",
                    name=op_name,
                    event_date=operation.start_date,
                    end_date=operation.end_date,
                    summary=operation.description,
                    region_id=operation.region_id,
                    operation_id=operation.id,
                    source="curated_seed",
                    confidence_level=0.91,
                )
                db.session.add(event)
                war_events[op_name] = event
        db.session.flush()
        return war_events

    # ── War Crimes ─────────────────────────────────────────────────────────

    def _seed_war_crimes(self, war_events: dict[str, WarEvent]):
        for item in WAR_CRIMES:
            event = war_events.get(item["war_event_name"])
            if not event:
                continue
            crime = WarCrime(
                war_event_id=event.id,
                category=item["category"],
                location_name=item.get("location_name"),
                victims=item.get("victims"),
                perpetrators=item.get("perpetrators"),
                death_toll=item.get("death_toll"),
                description=item.get("description"),
                sources=item.get("sources"),
                sensitivity_notes="Educational archival framing required.",
            )
            db.session.add(crime)
        db.session.flush()

    # ── Timeline Entries ───────────────────────────────────────────────────

    def _seed_timeline_entries(self, war_events: dict[str, WarEvent], regions: dict[str, GeographicRegion]):
        for event_name, event in war_events.items():
            entry = TimelineEntry(
                war_event_id=event.id,
                region_id=event.region_id,
                entry_type=event.event_type,
                headline=event.name,
                summary=event.summary,
                entry_date=event.event_date,
            )
            db.session.add(entry)
        db.session.flush()
