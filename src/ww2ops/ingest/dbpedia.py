from __future__ import annotations

from textwrap import dedent

from src.ww2ops.ingest.catalog import BATTLES, DBPEDIA_ENDPOINT, INTELLIGENCE_TOPICS, LEADERS, OPERATIONS
from src.ww2ops.ingest.utils import HttpCache, build_sparql_url, http_get_json


class DBpediaSource:
    def __init__(self, cache: HttpCache):
        self.cache = cache

    def query(self, sparql: str, *, force_refresh: bool = False):
        payload = http_get_json(
            build_sparql_url(DBPEDIA_ENDPOINT, sparql),
            headers={'Accept': 'application/sparql-results+json'},
            cache=self.cache,
            force_refresh=force_refresh,
        )
        return payload.get('results', {}).get('bindings', [])

    def fetch_abstracts(self, resource_names: list[str], *, force_refresh: bool = False):
        rows = []
        seen = set()
        for index in range(0, len(resource_names), 8):
            chunk = resource_names[index:index + 8]
            values = ' '.join(f'<http://dbpedia.org/resource/{name}>' for name in chunk)
            query = dedent(
                f"""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                SELECT ?resource ?abstract ?thumbnail WHERE {{
                  VALUES ?resource {{ {values} }}
                  OPTIONAL {{ ?resource dbo:abstract ?abstract FILTER(LANG(?abstract) = 'en') }}
                  OPTIONAL {{ ?resource dbo:thumbnail ?thumbnail }}
                }}
                """
            )
            for binding in self.query(query, force_refresh=force_refresh):
                resource = binding.get('resource', {}).get('value')
                if resource and resource in seen:
                    continue
                if resource:
                    seen.add(resource)
                rows.append(binding)
        return rows

    def fetch_all_enrichment(self, *, force_refresh: bool = False):
        resources = [
            *{item['dbpedia'] for item in LEADERS.values()},
            *{item['dbpedia'] for item in BATTLES.values()},
            *{item['dbpedia'] for item in OPERATIONS.values()},
            *{item['dbpedia'] for item in INTELLIGENCE_TOPICS.values()},
        ]
        return self.fetch_abstracts(resources, force_refresh=force_refresh)
