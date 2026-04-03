from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.ww2ops.db.models import Alliance, Battle, Campaign, CommandAssignment, GeographicRegion, ImportBatch, IntelligenceReport, Leader, Nation, Operation, ResourceBalance, ResourceSnapshot, ResourceType, WarCrime, WarEvent
from src.ww2ops.extensions import db
from src.ww2ops.ingest.catalog import BATTLES, COUNTRY_ALIASES, INTELLIGENCE_TOPICS, LEADER_ASSIGNMENTS, LEADERS, NATION_LABELS, OPERATIONS, PRIMARY_SIDES, REGION_ALIASES, SOURCE_METADATA
from src.ww2ops.ingest.cow import COWSource
from src.ww2ops.ingest.csv_ingestion import KaggleCSVSource
from src.ww2ops.ingest.dbpedia import DBpediaSource
from src.ww2ops.ingest.utils import HttpCache, first_value, normalize_headers, parse_float, parse_int, parse_point
from src.ww2ops.ingest.wikidata import WikidataSource


class HistoricalIngestionService:
    def __init__(self, cache_dir: str | Path | None = None):
        cache_path = Path(cache_dir or Path('instance') / 'ingest_cache')
        self.cache = HttpCache(cache_path)
        self.wikidata = WikidataSource(self.cache)
        self.dbpedia = DBpediaSource(self.cache)
        self.cow = COWSource(self.cache)
        self.kaggle = KaggleCSVSource()
        self.resource_types: dict[str, ResourceType] = {}

    def ingest_all(self, *, force_refresh: bool = False, kaggle_csv_path: str | None = None):
        self.ensure_core_records()
        summary = {}
        errors = {}
        steps = [
            ('cow_states', lambda: self.ingest_cow_states(force_refresh=force_refresh)),
            ('cow_alliances', lambda: self.ingest_cow_alliances(force_refresh=force_refresh)),
            ('wikidata_nations', lambda: self.ingest_wikidata_nations(force_refresh=force_refresh)),
            ('wikidata_leaders', lambda: self.ingest_wikidata_leaders(force_refresh=force_refresh)),
            ('wikidata_battles', lambda: self.ingest_wikidata_battles(force_refresh=force_refresh)),
            ('wikidata_operations', lambda: self.ingest_wikidata_operations(force_refresh=force_refresh)),
            ('dbpedia_enrichment', lambda: self.ingest_dbpedia_enrichment(force_refresh=force_refresh)),
            ('intelligence', lambda: self.ingest_intelligence_topics(force_refresh=force_refresh)),
            ('cow_nmc', lambda: self.ingest_cow_nmc(force_refresh=force_refresh)),
            ('cow_wars', lambda: self.ingest_cow_wars(force_refresh=force_refresh)),
            ('assignments', self.sync_command_assignments),
            ('war_crimes', self.ensure_aftermath_records),
        ]
        for name, step in steps:
            try:
                summary[name] = step()
            except Exception as exc:
                db.session.rollback()
                summary[name] = 0
                errors[name] = str(exc)
        if kaggle_csv_path:
            try:
                summary['kaggle_csv'] = self.ingest_kaggle_resource_csv(kaggle_csv_path)
            except Exception as exc:
                db.session.rollback()
                summary['kaggle_csv'] = 0
                errors['kaggle_csv'] = str(exc)
        if errors:
            summary['errors'] = errors
        return summary
    def ensure_core_records(self):
        self.resource_types = {item.code: item for item in ResourceType.query.all()}
        for code, name, unit, category in [('oil', 'Oil / Energy', 'energy units', 'strategic'), ('steel', 'Steel / Industrial Output', 'industrial units', 'strategic'), ('manpower', 'Military Manpower', 'personnel', 'human')]:
            item = self.resource_types.get(code)
            if item is None:
                item = ResourceType(code=code, name=name, unit=unit, category=category)
                db.session.add(item)
                db.session.flush()
                self.resource_types[code] = item
        for code, name, side, description in [('ALLIES', 'Allies', 'allies', 'World War II Allied coalition'), ('AXIS', 'Axis', 'axis', 'World War II Axis coalition'), ('NEUTRAL', 'Neutral', 'neutral', 'States outside the principal wartime coalitions')]:
            self._upsert_alliance(code=code, name=name, side=side, description=description, doctrine={'source': 'curated wartime bloc mapping'})
        db.session.commit()

    def ingest_cow_states(self, *, force_refresh: bool = False):
        batch = self._start_batch('Correlates of War State System Membership', 'api', {'year_window': [1939, 1945]})
        processed = 0
        for raw in self.cow.fetch_state_membership(force_refresh=force_refresh):
            row = normalize_headers(raw)
            name = self._canonical_name(first_value(row, ['statenme', 'state_name', 'statename', 'country', 'state']))
            if not name:
                continue
            start_year = parse_int(first_value(row, ['styear', 'start_year', 'year'])) or 1816
            end_year = parse_int(first_value(row, ['endyear', 'end_year'])) or 9999
            if start_year > 1945 or end_year < 1939:
                continue
            code = first_value(row, ['stateabb', 'state_abbr', 'abbr', 'abb']) or name[:3].upper()
            ccode = parse_int(first_value(row, ['ccode', 'cowcode', 'countrycode']))
            side = PRIMARY_SIDES.get(name, 'neutral')
            alliance = Alliance.query.filter_by(code='ALLIES' if side == 'allies' else 'AXIS' if side == 'axis' else 'NEUTRAL').one()
            self._upsert_nation(name=name, code=code, side=side, alliance=alliance, metadata={'cow_state_membership': {'ccode': ccode, 'abbr': code, 'start_year': start_year, 'end_year': end_year, **SOURCE_METADATA['cow_states']}})
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_cow_alliances(self, *, force_refresh: bool = False):
        batch = self._start_batch('Correlates of War Formal Alliances', 'api', {'year_window': [1939, 1945]})
        processed = 0
        ties_by_ccode: dict[int, int] = defaultdict(int)
        for raw in self.cow.fetch_alliances(force_refresh=force_refresh):
            row = normalize_headers(raw)
            start_year = parse_int(first_value(row, ['dyad_st_year', 'start_year', 'year', 'allyear', 'syear'])) or 1816
            end_year = parse_int(first_value(row, ['dyad_end_year', 'end_year'])) or 9999
            if start_year > 1945 or end_year < 1939:
                continue
            ccode = parse_int(first_value(row, ['ccode1', 'ccode', 'state1no', 'stateno', 'member']))
            if ccode is None:
                continue
            ties_by_ccode[ccode] += 1
            processed += 1
        for nation in Nation.query.all():
            ccode = ((nation.metadata_json or {}).get('cow_state_membership') or {}).get('ccode')
            if ccode is None:
                continue
            nation.metadata_json = self._merge_metadata(nation.metadata_json, {'cow_alliance_ties_1939_1945': {'tie_count': ties_by_ccode.get(ccode, 0), **SOURCE_METADATA['cow_alliances']}})
        for code in ('ALLIES', 'AXIS', 'NEUTRAL'):
            alliance = Alliance.query.filter_by(code=code).one()
            member_codes = [((nation.metadata_json or {}).get('cow_state_membership') or {}).get('ccode') for nation in Nation.query.filter_by(alliance_id=alliance.id).all()]
            alliance.doctrine = self._merge_metadata(alliance.doctrine, {'cow_metadata': {'member_ccodes': [value for value in member_codes if value is not None], 'dataset_window': '1939-1945', **SOURCE_METADATA['cow_alliances']}})
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed
    def ingest_wikidata_nations(self, *, force_refresh: bool = False):
        batch = self._start_batch('Wikidata Nations', 'api', {'records': len(NATION_LABELS)})
        processed = 0
        for binding in self.wikidata.fetch_nations(force_refresh=force_refresh):
            name = self._canonical_name(binding['label']['value'])
            if not name:
                continue
            self._upsert_nation(
                name=name,
                capital=binding.get('capitalLabel', {}).get('value'),
                description=binding.get('description', {}).get('value'),
                metadata={'wikidata': {'entity': binding['item']['value'].rsplit('/', 1)[-1], **SOURCE_METADATA['wikidata']}},
            )
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_wikidata_leaders(self, *, force_refresh: bool = False):
        batch = self._start_batch('Wikidata Leaders', 'api', {'records': len(LEADERS)})
        processed = 0
        for binding in self.wikidata.fetch_leaders(force_refresh=force_refresh):
            name = binding['label']['value']
            config = LEADERS.get(name)
            if not config:
                continue
            nation = self._find_nation(config['country'])
            if nation is None:
                continue
            leader = Leader.query.filter_by(name=name, nation_id=nation.id).first()
            if leader is None:
                leader = Leader(name=name, nation_id=nation.id)
                db.session.add(leader)
            leader.title = leader.title or config['role_type'].title()
            leader.role_type = config['role_type']
            leader.biography = binding.get('description', {}).get('value') or leader.biography
            leader.ideology = leader.ideology or f"WWII {config['role_type']} leadership"
            leader.portrait_url = binding.get('image', {}).get('value') or leader.portrait_url
            leader.influence_score = leader.influence_score or self._influence_score_for_leader(name, config['role_type'])
            leader.born_on = self._parse_date_value(binding.get('born', {}).get('value')) or leader.born_on
            leader.died_on = self._parse_date_value(binding.get('died', {}).get('value')) or leader.died_on
            leader.metadata_json = self._merge_metadata(leader.metadata_json, {'wikidata': {'entity': binding['item']['value'].rsplit('/', 1)[-1], **SOURCE_METADATA['wikidata']}, 'key_operations': LEADER_ASSIGNMENTS.get(name, [])})
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_wikidata_battles(self, *, force_refresh: bool = False):
        batch = self._start_batch('Wikidata Battles', 'api', {'records': len(BATTLES)})
        processed = 0
        for binding in self.wikidata.fetch_battles(force_refresh=force_refresh):
            name = binding['label']['value']
            config = BATTLES.get(name)
            if not config:
                continue
            latitude, longitude = parse_point(binding.get('coord', {}).get('value'))
            region = self._get_or_create_region(config['region'], theater=self._theater_for_region(config['region']), latitude=latitude, longitude=longitude)
            campaign_label = binding.get('campaignLabel', {}).get('value') or f"{config['region']} Campaign"
            campaign = self._upsert_campaign(campaign_label, region=region, theater=self._theater_for_region(config['region']))
            battle = Battle.query.filter_by(name=name).first()
            if battle is None:
                battle = Battle(name=name, start_date=self._parse_datetime_value(binding.get('start', {}).get('value')) or datetime(1940, 1, 1))
                db.session.add(battle)
            battle.campaign_id = campaign.id
            battle.region_id = region.id
            battle.location_name = binding.get('locationLabel', {}).get('value') or region.name
            battle.start_date = self._parse_datetime_value(binding.get('start', {}).get('value')) or battle.start_date
            battle.end_date = self._parse_datetime_value(binding.get('end', {}).get('value')) or battle.end_date
            battle.description = binding.get('description', {}).get('value') or battle.description
            battle.victor_side = config['victor_side']
            battle.axis_casualties = config.get('axis_casualties') or battle.axis_casualties
            battle.allied_casualties = config.get('allied_casualties') or battle.allied_casualties
            battle.latitude = latitude or battle.latitude
            battle.longitude = longitude or battle.longitude
            battle.metadata_json = self._merge_metadata(battle.metadata_json, {'wikidata': {'entity': binding['item']['value'].rsplit('/', 1)[-1], **SOURCE_METADATA['wikidata']}})
            self._upsert_war_event(event_type='battle', name=name, event_date=battle.start_date, end_date=battle.end_date, summary=battle.description, region=region, source_meta=SOURCE_METADATA['wikidata'], battle=battle)
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_wikidata_operations(self, *, force_refresh: bool = False):
        batch = self._start_batch('Wikidata Operations', 'api', {'records': len(OPERATIONS)})
        processed = 0
        for binding in self.wikidata.fetch_operations(force_refresh=force_refresh):
            name = binding['label']['value']
            config = OPERATIONS.get(name)
            if not config:
                continue
            latitude, longitude = parse_point(binding.get('coord', {}).get('value'))
            region = self._get_or_create_region(config['region'], theater=self._theater_for_region(config['region']), latitude=latitude, longitude=longitude)
            campaign = self._upsert_campaign(config['campaign'], region=region, theater=self._theater_for_region(config['region']))
            operation = Operation.query.filter_by(name=name).first()
            if operation is None:
                operation = Operation(name=name, start_date=self._parse_datetime_value(binding.get('start', {}).get('value')) or datetime(1940, 1, 1))
                db.session.add(operation)
            operation.campaign_id = campaign.id
            operation.region_id = region.id
            operation.code_name = config['code_name']
            operation.side = config['side']
            operation.objective = binding.get('description', {}).get('value') or operation.objective
            operation.outcome = config['outcome']
            operation.start_date = self._parse_datetime_value(binding.get('start', {}).get('value')) or operation.start_date
            operation.end_date = self._parse_datetime_value(binding.get('end', {}).get('value')) or operation.end_date
            operation.description = binding.get('description', {}).get('value') or operation.description
            operation.analysis = operation.analysis or f"Imported from external datasets for {name}."
            operation.intelligence_notes = operation.intelligence_notes or f"Operational record aligned to {region.name}."
            operation.parameters = self._merge_metadata(operation.parameters, {'location_label': binding.get('locationLabel', {}).get('value'), 'source': SOURCE_METADATA['wikidata']['source']})
            self._upsert_war_event(event_type='operation', name=name, event_date=operation.start_date, end_date=operation.end_date, summary=operation.description, region=region, source_meta=SOURCE_METADATA['wikidata'], operation=operation)
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed
    def ingest_dbpedia_enrichment(self, *, force_refresh: bool = False):
        batch = self._start_batch('DBpedia Enrichment', 'api', {})
        processed = 0
        leader_lookup = {config['dbpedia']: name for name, config in LEADERS.items()}
        battle_lookup = {config['dbpedia']: name for name, config in BATTLES.items()}
        operation_lookup = {config['dbpedia']: name for name, config in OPERATIONS.items()}
        for binding in self.dbpedia.fetch_all_enrichment(force_refresh=force_refresh):
            resource_name = binding['resource']['value'].rsplit('/', 1)[-1]
            abstract = binding.get('abstract', {}).get('value')
            thumbnail = binding.get('thumbnail', {}).get('value')
            if resource_name in leader_lookup:
                leader = Leader.query.filter_by(name=leader_lookup[resource_name]).first()
                if leader and (abstract or thumbnail):
                    if abstract:
                        leader.biography = abstract
                    if thumbnail and not leader.portrait_url:
                        leader.portrait_url = thumbnail
                    leader.metadata_json = self._merge_metadata(leader.metadata_json, {'dbpedia': {**SOURCE_METADATA['dbpedia'], 'thumbnail_available': bool(thumbnail), 'abstract_available': bool(abstract)}})
                    processed += 1
            elif resource_name in battle_lookup:
                battle = Battle.query.filter_by(name=battle_lookup[resource_name]).first()
                if battle and (abstract or thumbnail):
                    if abstract:
                        battle.description = abstract
                    battle.metadata_json = self._merge_metadata(battle.metadata_json, {'dbpedia': {**SOURCE_METADATA['dbpedia'], 'thumbnail': thumbnail}})
                    processed += 1
            elif resource_name in operation_lookup:
                operation = Operation.query.filter_by(name=operation_lookup[resource_name]).first()
                if operation and (abstract or thumbnail):
                    if abstract:
                        operation.description = abstract
                        operation.analysis = abstract
                    operation.parameters = self._merge_metadata(operation.parameters, {'dbpedia': {**SOURCE_METADATA['dbpedia'], 'thumbnail': thumbnail}})
                    processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed
    def ingest_intelligence_topics(self, *, force_refresh: bool = False):
        batch = self._start_batch('Wikidata Intelligence Topics', 'api', {'records': len(INTELLIGENCE_TOPICS)})
        processed = 0
        for binding in self.wikidata.fetch_intelligence_topics(force_refresh=force_refresh):
            label = binding['label']['value']
            config = INTELLIGENCE_TOPICS.get(label)
            if not config:
                continue
            nation = self._find_nation(config['nation'])
            region = self._get_or_create_region(config['region'], theater=self._theater_for_region(config['region']))
            report = IntelligenceReport.query.filter_by(source_reference=label).first()
            if report is None:
                report = IntelligenceReport(report_date=self._parse_datetime_value(binding.get('start', {}).get('value')) or datetime(1944, 1, 1))
                db.session.add(report)
            report.nation_id = nation.id if nation else None
            report.region_id = region.id
            report.classification = config['classification']
            report.source_type = 'historical_intelligence_topic'
            report.report_type = config['report_type']
            report.content = binding.get('description', {}).get('value') or label
            report.decoded = config['report_type'] in {'signals_intelligence', 'deception'}
            report.confidence_level = SOURCE_METADATA['wikidata']['confidence']
            report.source_reference = label
            report.metadata_json = self._merge_metadata(report.metadata_json, {'wikidata': SOURCE_METADATA['wikidata']})
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_cow_nmc(self, *, force_refresh: bool = False):
        batch = self._start_batch('Correlates of War National Material Capabilities', 'api', {'year_window': [1939, 1945]})
        processed = 0
        ccode_to_nation = {((nation.metadata_json or {}).get('cow_state_membership') or {}).get('ccode'): nation for nation in Nation.query.all()}
        for raw in self.cow.fetch_nmc(force_refresh=force_refresh):
            row = normalize_headers(raw)
            year = parse_int(first_value(row, ['year']))
            if not year or year < 1939 or year > 1945:
                continue
            nation = ccode_to_nation.get(parse_int(first_value(row, ['ccode', 'statecode'])))
            if nation is None:
                continue
            oil = parse_float(first_value(row, ['pec', 'energy_consumption']))
            steel = parse_float(first_value(row, ['irst', 'steel', 'iron_steel']))
            manpower = parse_float(first_value(row, ['milper', 'manpower', 'tpop']))
            cinc = parse_float(first_value(row, ['cinc']))
            metrics = {
                'cinc': cinc,
                'military_expenditure': parse_float(first_value(row, ['milex', 'military_expenditure'])),
                'total_population': parse_float(first_value(row, ['tpop', 'total_population'])),
                'urban_population': parse_float(first_value(row, ['upop', 'urban_population'])),
                'energy_consumption': oil,
                'steel_output': steel,
                'morale': self._morale_from_capabilities(nation.side, cinc),
                'territory_count': 1,
                **SOURCE_METADATA['cow_nmc'],
            }
            self._upsert_resource_snapshot(nation=nation, snapshot_date=datetime(year, 1, 1), oil=oil, steel=steel, manpower=manpower, metrics=metrics, source=SOURCE_METADATA['cow_nmc']['source'], confidence=SOURCE_METADATA['cow_nmc']['confidence'])
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_cow_wars(self, *, force_refresh: bool = False):
        batch = self._start_batch('Correlates of War Inter-State Wars', 'api', {'year_window': [1939, 1945]})
        processed = 0
        for raw in self.cow.fetch_wars(force_refresh=force_refresh):
            row = normalize_headers(raw)
            start_year = parse_int(first_value(row, ['startyear1', 'start_year', 'startyear']))
            if not start_year or start_year < 1939 or start_year > 1945:
                continue
            name = first_value(row, ['warname', 'name']) or 'Unnamed war event'
            end_year = parse_int(first_value(row, ['endyear1', 'end_year', 'endyear'])) or start_year
            region_name = self._infer_region_from_text(name)
            region = self._get_or_create_region(region_name, theater=self._theater_for_region(region_name))
            self._upsert_war_event(event_type='war', name=name, event_date=datetime(start_year, 1, 1), end_date=datetime(end_year, 12, 31), summary=f"Imported interstate war record for {name}.", region=region, source_meta=SOURCE_METADATA['cow_wars'])
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def ingest_kaggle_resource_csv(self, csv_path: str):
        batch = self._start_batch('Kaggle CSV Resource Import', 'csv', {'path': csv_path})
        processed = 0
        for row in self.kaggle.normalize_resource_rows(self.kaggle.read_rows(csv_path)):
            nation = self._find_nation(row['nation'])
            if nation is None:
                continue
            self._upsert_resource_snapshot(nation=nation, snapshot_date=datetime(int(row['year']), 1, 1), oil=row['oil'], steel=row['steel'], manpower=row['manpower'], metrics={'gdp': row['gdp'], 'morale': row['morale'], 'territory_count': 1, 'source': row['source']}, source=row['source'], confidence=row['confidence'])
            processed += 1
        db.session.commit()
        self._finish_batch(batch, processed)
        return processed

    def sync_command_assignments(self):
        processed = 0
        for leader_name, entries in LEADER_ASSIGNMENTS.items():
            leader = Leader.query.filter_by(name=leader_name).first()
            if leader is None:
                continue
            for item_name in entries:
                operation = Operation.query.filter_by(name=item_name).first()
                campaign = Campaign.query.filter_by(name=item_name).first()
                existing = CommandAssignment.query.filter_by(leader_id=leader.id, operation_id=operation.id if operation else None, campaign_id=campaign.id if campaign else None).first()
                if existing is None:
                    existing = CommandAssignment(leader_id=leader.id, operation_id=operation.id if operation else None, campaign_id=campaign.id if campaign else None)
                    db.session.add(existing)
                existing.position = existing.position or leader.role_type.title()
                existing.start_date = existing.start_date or (operation.start_date if operation else campaign.start_date if campaign else None)
                existing.end_date = existing.end_date or (operation.end_date if operation else campaign.end_date if campaign else None)
                existing.notes = existing.notes or f"Linked from curated wartime leadership assignment map for {leader_name}."
                processed += 1
        db.session.commit()
        return processed

    def ensure_aftermath_records(self):
        if WarCrime.query.count():
            return WarCrime.query.count()
        europe = self._get_or_create_region('Europe', theater='Europe')
        event = self._upsert_war_event(event_type='war_crime', name='Oradour-sur-Glane massacre', event_date=datetime(1944, 6, 10), end_date=None, summary='Mass killing of civilians by SS forces in occupied France.', region=europe, source_meta={'source': 'Curated archival synthesis', 'confidence': 0.9})
        crime = WarCrime.query.filter_by(war_event_id=event.id).first()
        if crime is None:
            crime = WarCrime(war_event_id=event.id)
            db.session.add(crime)
        crime.category = 'massacre'
        crime.location_name = 'Oradour-sur-Glane, France'
        crime.victims = 'Civilians of Oradour-sur-Glane'
        crime.perpetrators = '2nd SS Panzer Division Das Reich'
        crime.death_toll = 643
        crime.description = 'The village population was murdered and the settlement destroyed.'
        crime.sources = ['French national memorial archives', 'Postwar tribunal summaries']
        crime.media_url = 'img/aftermath/newspaper_texture.jpg'
        crime.sensitivity_notes = 'Educational archival framing required.'
        db.session.commit()
        return WarCrime.query.count()
    def _upsert_alliance(self, *, code: str, name: str, side: str, description: str, doctrine: dict[str, Any]):
        alliance = Alliance.query.filter_by(code=code).first()
        if alliance is None:
            alliance = Alliance(code=code, name=name, side=side)
            db.session.add(alliance)
        alliance.name = name
        alliance.side = side
        alliance.description = description
        alliance.doctrine = self._merge_metadata(alliance.doctrine, doctrine)
        db.session.flush()
        return alliance

    def _upsert_nation(self, *, name: str, code: str | None = None, side: str | None = None, alliance: Alliance | None = None, capital: str | None = None, description: str | None = None, metadata: dict[str, Any] | None = None):
        nation = self._find_nation(name)
        if nation is None:
            nation = Nation(name=name, code=(code or name[:3].upper())[:16])
            db.session.add(nation)
        if code:
            nation.code = code[:16]
        if side:
            nation.side = side
        if alliance:
            nation.alliance_id = alliance.id
        if capital:
            nation.capital = capital
        if description:
            nation.description = description
        if metadata:
            nation.metadata_json = self._merge_metadata(nation.metadata_json, metadata)
        db.session.flush()
        return nation

    def _upsert_campaign(self, name: str, *, region: GeographicRegion | None, theater: str | None):
        campaign = Campaign.query.filter_by(name=name).first()
        if campaign is None:
            campaign = Campaign(name=name)
            db.session.add(campaign)
        if region:
            campaign.region_id = region.id
        if theater:
            campaign.theater = theater
        if campaign.description is None:
            campaign.description = f"Imported campaign context for {name}."
        db.session.flush()
        return campaign

    def _upsert_war_event(self, *, event_type: str, name: str, event_date: datetime, end_date: datetime | None, summary: str | None, region: GeographicRegion | None, source_meta: dict[str, Any], battle: Battle | None = None, operation: Operation | None = None):
        event = WarEvent.query.filter_by(event_type=event_type, name=name, event_date=event_date).first()
        if event is None:
            event = WarEvent(event_type=event_type, name=name, event_date=event_date)
            db.session.add(event)
        event.end_date = end_date
        event.summary = summary
        event.region_id = region.id if region else None
        event.battle_id = battle.id if battle else event.battle_id
        event.operation_id = operation.id if operation else event.operation_id
        event.source = source_meta.get('source')
        event.confidence_level = source_meta.get('confidence')
        db.session.flush()
        return event

    def _upsert_resource_snapshot(self, *, nation: Nation, snapshot_date: datetime, oil: float | None, steel: float | None, manpower: float | None, metrics: dict[str, Any], source: str, confidence: float, simulation_id: int | None = None):
        snapshot = ResourceSnapshot.query.filter_by(nation_id=nation.id, simulation_id=simulation_id, snapshot_date=snapshot_date).first()
        if snapshot is None:
            snapshot = ResourceSnapshot(nation_id=nation.id, simulation_id=simulation_id, snapshot_date=snapshot_date)
            db.session.add(snapshot)
            db.session.flush()
        snapshot.source = source
        snapshot.confidence_level = confidence
        snapshot.metrics = self._merge_metadata(snapshot.metrics, metrics)
        for code, amount in {'oil': oil, 'steel': steel, 'manpower': manpower}.items():
            if amount is None:
                continue
            balance = ResourceBalance.query.filter_by(snapshot_id=snapshot.id, resource_type_id=self.resource_types[code].id).first()
            if balance is None:
                balance = ResourceBalance(snapshot_id=snapshot.id, resource_type_id=self.resource_types[code].id)
                db.session.add(balance)
            balance.amount = float(amount)
        db.session.flush()
        return snapshot

    def _find_nation(self, name: str | None):
        canonical = self._canonical_name(name)
        return Nation.query.filter_by(name=canonical).first() if canonical else None

    def _canonical_name(self, name: str | None):
        if not name:
            return None
        normalized = name.strip()
        return COUNTRY_ALIASES.get(normalized, normalized)

    def _get_or_create_region(self, name: str, *, theater: str | None = None, latitude: float | None = None, longitude: float | None = None):
        canonical_name = REGION_ALIASES.get(name, name)
        region = GeographicRegion.query.filter_by(name=canonical_name).first()
        if region is None:
            region = GeographicRegion(name=canonical_name, theater=theater or self._theater_for_region(canonical_name))
            db.session.add(region)
        region.theater = theater or region.theater or self._theater_for_region(canonical_name)
        region.latitude = latitude or region.latitude
        region.longitude = longitude or region.longitude
        db.session.flush()
        return region

    def _parse_datetime_value(self, value: str | None):
        if not value:
            return None
        cleaned = value.replace('Z', '+00:00')
        try:
            return datetime.fromisoformat(cleaned)
        except ValueError:
            try:
                return datetime.strptime(value[:10], '%Y-%m-%d')
            except ValueError:
                return None

    def _parse_date_value(self, value: str | None):
        parsed = self._parse_datetime_value(value)
        return parsed.date() if parsed else None

    def _influence_score_for_leader(self, name: str, role_type: str):
        return min(98, (84 if role_type == 'political' else 88) + (sum(ord(char) for char in name[:3]) % 10))

    def _morale_from_capabilities(self, side: str | None, cinc: float | None):
        baseline = 58 if side == 'axis' else 68 if side == 'allies' else 50
        return baseline if cinc is None else max(30, min(90, baseline + int(cinc * 100)))

    def _theater_for_region(self, region_name: str | None):
        name = (region_name or '').lower()
        if any(token in name for token in ['pacific', 'midway', 'japan']):
            return 'Pacific'
        if any(token in name for token in ['africa', 'alamein']):
            return 'Africa'
        if any(token in name for token in ['china', 'asia', 'burma']):
            return 'Asia'
        return 'Europe'

    def _infer_region_from_text(self, text: str):
        lowered = text.lower()
        if 'pacific' in lowered or 'japan' in lowered:
            return 'Pacific'
        if 'africa' in lowered or 'el alamein' in lowered:
            return 'North Africa'
        return 'Europe'

    def _merge_metadata(self, current: dict[str, Any] | None, incoming: dict[str, Any] | None):
        merged = dict(current or {})
        for key, value in (incoming or {}).items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged

    def _start_batch(self, source_name: str, source_type: str, metadata: dict[str, Any]):
        batch = ImportBatch(source_name=source_name, source_type=source_type, status='running', metadata_json=metadata)
        db.session.add(batch)
        db.session.commit()
        return batch

    def _finish_batch(self, batch: ImportBatch, records_processed: int):
        batch.records_processed = records_processed
        batch.status = 'completed'
        db.session.commit()




