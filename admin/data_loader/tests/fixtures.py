import os
import sqlite3
from pathlib import Path

import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


postgres_dsl = {
    "dbname": os.environ.get("POSTGRES_DB", "postgres"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "postgres"),
    "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "options": "-c search_path=content",
}

sqlitedb_path = os.environ.get("SQLITE_FILE", BASE_DIR / "db.sqlite")


@pytest.fixture(scope="session")
def pg_cursor():
    with psycopg2.connect(**postgres_dsl) as pg_conn:
        cursor = pg_conn.cursor()
        yield cursor


@pytest.fixture(scope="session")
def sqlite_cursor():
    with sqlite3.connect(sqlitedb_path) as sqlite_conn:
        cursor = sqlite_conn.cursor()
        yield cursor
