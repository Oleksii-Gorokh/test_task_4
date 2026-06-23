from __future__ import annotations

from pathlib import Path

import pytest

from registration_port.db import initialize_database


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "data" / "schema.sqlite.sql"
SEED_PATH = PROJECT_ROOT / "data" / "seed.sqlite.sql"


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "registration.sqlite3"
    initialize_database(path, SCHEMA_PATH, SEED_PATH)
    return path
