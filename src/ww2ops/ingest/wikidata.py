from __future__ import annotations

from textwrap import dedent

from src.ww2ops.ingest.catalog import BATTLES, INTELLIGENCE_TOPICS, LEADERS, NATION_LABELS, OPERATIONS, WIKIDATA_ENDPOINT
from src.ww2ops.ingest.utils import HttpCache, build_sparql_url, http_get_json


class WikidataSource:
    def __init__(self, cache: HttpCache):
        self.cache = cache

    def query(self, sparql: str, *, force_refresh: bool = False):
        payload = http_get_json(
            build_sparql_url(WIKIDATA_ENDPOINT, sparql),
            headers={'Accept': 'application/sparql-results+json'},
            cache=self.cache,
            force_refresh=force_refresh,
        )
        return payload.get('results', {}).get('bindings', [])

    def _fetch_by_labels(self, labels: list[str], query_builder, *, force_refresh: bool = False, chunk_size: int = 4):
        rows = []
        seen_entities = set()
        for index in range(0, len(labels), chunk_size):
            chunk = labels[index:index + chunk_size]
            for binding in self.query(query_builder(chunk), force_refresh=force_refresh):
                entity = binding.get('item', {}).get('value')
                if entity and entity in seen_entities:
                    continue
                if entity:
                    seen_entities.add(entity)
                rows.append(binding)
        return rows

    def fetch_nations(self, *, force_refresh: bool = False):
        def build_query(chunk: list[str]):
            values = ' '.join(f'"{label}"@en' for label in chunk)
            return dedent(
                f"""
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?item ?label ?description ?capitalLabel ?coord WHERE {{
                  VALUES ?label {{ {values} }}
                  ?item rdfs:label ?label .
                  FILTER(LANG(?label) = 'en')
                  OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description) = 'en') }}
                  OPTIONAL {{ ?item wdt:P36 ?capital . ?capital rdfs:label ?capitalLabel FILTER(LANG(?capitalLabel) = 'en') }}
                  OPTIONAL {{ ?item wdt:P625 ?coord }}
                }}
                """
            )

        return self._fetch_by_labels(list(NATION_LABELS.values()), build_query, force_refresh=force_refresh, chunk_size=6)

    def fetch_leaders(self, *, force_refresh: bool = False):
        def build_query(chunk: list[str]):
            values = ' '.join(f'"{label}"@en' for label in chunk)
            return dedent(
                f"""
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?item ?label ?description ?countryLabel ?born ?died ?image WHERE {{
                  VALUES ?label {{ {values} }}
                  ?item rdfs:label ?label .
                  FILTER(LANG(?label) = 'en')
                  OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description) = 'en') }}
                  OPTIONAL {{ ?item wdt:P27 ?country . ?country rdfs:label ?countryLabel FILTER(LANG(?countryLabel) = 'en') }}
                  OPTIONAL {{ ?item wdt:P569 ?born }}
                  OPTIONAL {{ ?item wdt:P570 ?died }}
                  OPTIONAL {{ ?item wdt:P18 ?image }}
                }}
                """
            )

        return self._fetch_by_labels(list(LEADERS.keys()), build_query, force_refresh=force_refresh, chunk_size=3)

    def fetch_battles(self, *, force_refresh: bool = False):
        def build_query(chunk: list[str]):
            values = ' '.join(f'"{label}"@en' for label in chunk)
            return dedent(
                f"""
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?item ?label ?description ?start ?end ?locationLabel ?coord ?campaignLabel WHERE {{
                  VALUES ?label {{ {values} }}
                  ?item rdfs:label ?label .
                  FILTER(LANG(?label) = 'en')
                  OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description) = 'en') }}
                  OPTIONAL {{ ?item wdt:P580 ?start }}
                  OPTIONAL {{ ?item wdt:P582 ?end }}
                  OPTIONAL {{ ?item wdt:P276 ?location . ?location rdfs:label ?locationLabel FILTER(LANG(?locationLabel) = 'en') }}
                  OPTIONAL {{ ?item wdt:P625 ?coord }}
                  OPTIONAL {{ ?item wdt:P361 ?campaign . ?campaign rdfs:label ?campaignLabel FILTER(LANG(?campaignLabel) = 'en') }}
                }}
                """
            )

        return self._fetch_by_labels(list(BATTLES.keys()), build_query, force_refresh=force_refresh, chunk_size=3)

    def fetch_operations(self, *, force_refresh: bool = False):
        def build_query(chunk: list[str]):
            values = ' '.join(f'"{label}"@en' for label in chunk)
            return dedent(
                f"""
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?item ?label ?description ?start ?end ?locationLabel ?coord WHERE {{
                  VALUES ?label {{ {values} }}
                  ?item rdfs:label ?label .
                  FILTER(LANG(?label) = 'en')
                  OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description) = 'en') }}
                  OPTIONAL {{ ?item wdt:P580 ?start }}
                  OPTIONAL {{ ?item wdt:P582 ?end }}
                  OPTIONAL {{ ?item wdt:P276 ?location . ?location rdfs:label ?locationLabel FILTER(LANG(?locationLabel) = 'en') }}
                  OPTIONAL {{ ?item wdt:P625 ?coord }}
                }}
                """
            )

        return self._fetch_by_labels(list(OPERATIONS.keys()), build_query, force_refresh=force_refresh, chunk_size=3)

    def fetch_intelligence_topics(self, *, force_refresh: bool = False):
        def build_query(chunk: list[str]):
            values = ' '.join(f'"{label}"@en' for label in chunk)
            return dedent(
                f"""
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?item ?label ?description ?start ?end WHERE {{
                  VALUES ?label {{ {values} }}
                  ?item rdfs:label ?label .
                  FILTER(LANG(?label) = 'en')
                  OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description) = 'en') }}
                  OPTIONAL {{ ?item wdt:P580 ?start }}
                  OPTIONAL {{ ?item wdt:P582 ?end }}
                }}
                """
            )

        return self._fetch_by_labels(list(INTELLIGENCE_TOPICS.keys()), build_query, force_refresh=force_refresh, chunk_size=3)
