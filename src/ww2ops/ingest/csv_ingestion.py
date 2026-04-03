from __future__ import annotations

import csv
import subprocess
from pathlib import Path

from src.ww2ops.ingest.catalog import KAGGLE_RESOURCE_COLUMN_ALIASES
from src.ww2ops.ingest.utils import first_value, normalize_headers, parse_float, parse_int


class KaggleCSVSource:
    def read_rows(self, csv_path: str | Path):
        path = Path(csv_path)
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            return [normalize_headers(row) for row in reader]

    def normalize_resource_rows(self, rows: list[dict[str, str]]):
        normalized_rows = []
        for row in rows:
            nation = first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['nation'])
            year = parse_int(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['year']))
            if not nation or not year:
                continue
            normalized_rows.append({
                'nation': nation,
                'year': year,
                'oil': parse_float(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['oil'])),
                'steel': parse_float(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['steel'])),
                'manpower': parse_float(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['manpower'])),
                'gdp': parse_float(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['gdp'])),
                'morale': parse_float(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['morale'])),
                'source': first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['source']) or 'Kaggle CSV dataset',
                'confidence': parse_float(first_value(row, KAGGLE_RESOURCE_COLUMN_ALIASES['confidence'])) or 0.72,
            })
        return normalized_rows

    def download_with_cli(self, dataset_slug: str, destination_dir: str | Path):
        destination = Path(destination_dir)
        destination.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', dataset_slug, '-p', str(destination), '--unzip'],
            check=True,
            text=True,
        )
        return destination
