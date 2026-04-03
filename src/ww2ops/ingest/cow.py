from __future__ import annotations

from src.ww2ops.ingest.catalog import COW_URLS
from src.ww2ops.ingest.utils import HttpCache, load_csv_rows_from_url, load_csv_rows_from_zip_url


class COWSource:
    def __init__(self, cache: HttpCache):
        self.cache = cache

    def fetch_state_membership(self, *, force_refresh: bool = False):
        return load_csv_rows_from_zip_url(
            COW_URLS['states'],
            preferred_members=['states', 'state_system', 'membership'],
            cache=self.cache,
            force_refresh=force_refresh,
        )

    def fetch_nmc(self, *, force_refresh: bool = False):
        return load_csv_rows_from_zip_url(
            COW_URLS['nmc'],
            preferred_members=['nmc', 'capabilities'],
            cache=self.cache,
            force_refresh=force_refresh,
        )

    def fetch_alliances(self, *, force_refresh: bool = False):
        return load_csv_rows_from_zip_url(
            COW_URLS['alliances'],
            preferred_members=['member_yearly', 'member', 'alliance'],
            cache=self.cache,
            force_refresh=force_refresh,
        )

    def fetch_wars(self, *, force_refresh: bool = False):
        return load_csv_rows_from_url(COW_URLS['wars'], cache=self.cache, force_refresh=force_refresh)
