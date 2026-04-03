from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import time
import zipfile
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


USER_AGENT = 'ChronoConflict/1.0 (+historical data ingestion)'
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}


class RemoteFetchError(RuntimeError):
    pass


class HttpCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, url: str) -> bytes | None:
        path = self._path_for(url)
        return path.read_bytes() if path.exists() else None

    def set(self, url: str, payload: bytes) -> bytes:
        path = self._path_for(url)
        path.write_bytes(payload)
        return payload

    def _path_for(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode('utf-8')).hexdigest()
        suffix = Path(url.split('?')[0]).suffix or '.bin'
        return self.cache_dir / f'{digest}{suffix}'


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, HTTPError):
        return exc.code in TRANSIENT_HTTP_CODES
    return isinstance(exc, URLError)


def http_get(url: str, *, headers: dict[str, str] | None = None, cache: HttpCache | None = None, force_refresh: bool = False) -> bytes:
    cached = cache.get(url) if cache else None
    if cached is not None and not force_refresh:
        return cached

    request_headers = {'User-Agent': USER_AGENT, **(headers or {})}
    request = Request(url, headers=request_headers)
    last_exc = None
    for attempt in range(1, 4):
        try:
            with urlopen(request, timeout=45) as response:
                payload = response.read()
            return cache.set(url, payload) if cache else payload
        except Exception as exc:
            last_exc = exc
            if attempt < 3 and _is_retryable(exc):
                time.sleep(1.5 * attempt)
                continue
            break

    if cached is not None:
        return cached
    raise RemoteFetchError(f'Failed to fetch {url}: {last_exc}') from last_exc


def http_get_json(url: str, *, headers: dict[str, str] | None = None, cache: HttpCache | None = None, force_refresh: bool = False):
    payload = http_get(url, headers=headers, cache=cache, force_refresh=force_refresh)
    return json.loads(payload.decode('utf-8'))


def load_csv_rows_from_url(url: str, *, cache: HttpCache | None = None, force_refresh: bool = False) -> list[dict[str, str]]:
    payload = http_get(url, cache=cache, force_refresh=force_refresh)
    text = payload.decode('utf-8-sig', errors='replace')
    return list(csv.DictReader(text.splitlines()))


def load_csv_rows_from_zip_url(url: str, *, preferred_members: Iterable[str] | None = None, cache: HttpCache | None = None, force_refresh: bool = False) -> list[dict[str, str]]:
    payload = http_get(url, cache=cache, force_refresh=force_refresh)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        names = zf.namelist()
        selected = None
        if preferred_members:
            lowered_preferences = [item.lower() for item in preferred_members]
            for name in names:
                lowered_name = name.lower()
                if lowered_name.endswith('.csv') and any(pref in lowered_name for pref in lowered_preferences):
                    selected = name
                    break
        if selected is None:
            selected = next((name for name in names if name.lower().endswith('.csv')), None)
        if selected is None:
            raise RemoteFetchError(f'No CSV member found in archive {url}')
        with zf.open(selected) as handle:
            text = handle.read().decode('utf-8-sig', errors='replace')
    return list(csv.DictReader(text.splitlines()))


def normalize_headers(row: dict[str, str]) -> dict[str, str]:
    normalized = {}
    for key, value in row.items():
        normalized[re.sub(r'[^a-z0-9]+', '_', (key or '').strip().lower()).strip('_')] = (value or '').strip()
    return normalized


def first_value(row: dict[str, str], aliases: Iterable[str]) -> str | None:
    for alias in aliases:
        key = re.sub(r'[^a-z0-9]+', '_', alias.strip().lower()).strip('_')
        if key in row and row[key] not in {'', None}:
            return row[key]
    return None


def parse_int(value: str | None) -> int | None:
    if value in {None, '', 'NA', 'N/A', '-9', '-8'}:
        return None
    cleaned = re.sub(r'[^0-9\-]', '', value)
    return int(cleaned) if cleaned not in {'', '-'} else None


def parse_float(value: str | None) -> float | None:
    if value in {None, '', 'NA', 'N/A', '-9', '-8'}:
        return None
    cleaned = re.sub(r'[^0-9.\-]', '', value)
    return float(cleaned) if cleaned not in {'', '-', '.'} else None


def parse_point(value: str | None) -> tuple[float | None, float | None]:
    if not value:
        return None, None
    match = re.search(r'Point\(([-0-9.]+) ([-0-9.]+)\)', value)
    if not match:
        return None, None
    longitude = float(match.group(1))
    latitude = float(match.group(2))
    return latitude, longitude


def build_sparql_url(endpoint: str, query: str) -> str:
    return f"{endpoint}?{urlencode({'query': query, 'format': 'json'})}"

