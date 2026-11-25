"""Fixtures for the database tests.

Most tests use mongomock (no server needed). Tests marked ``mongo`` need a
real MongoDB, because mongomock ignores validators and TTL indexes; they are
skipped when none is reachable at ``MONGO_TEST_URI``
(default ``mongodb://localhost:27017``).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import mongomock
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.db.seed import load_seed

FAST_ROUNDS = 4
SEED_TIME = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "mongo: needs a real MongoDB server (skipped when none is reachable)"
    )


@pytest.fixture
def mock_db():
    """An empty mongomock database whose name ends in _test."""
    client = mongomock.MongoClient(tz_aware=True)
    yield client["hoteltrivago_test"]
    client.close()


@pytest.fixture
def seeded_mock_db(mock_db):
    """A mongomock database with the seed loaded."""
    load_seed(mock_db, validators=False, now=SEED_TIME, rounds=FAST_ROUNDS)
    return mock_db


@pytest.fixture(scope="session")
def mongo_client():
    uri = os.environ.get("MONGO_TEST_URI", "mongodb://localhost:27017")
    client = MongoClient(uri, tz_aware=True, serverSelectionTimeoutMS=1500)
    try:
        client.admin.command("ping")
    except PyMongoError:
        client.close()
        pytest.skip(f"no MongoDB reachable at {uri}")
    yield client
    client.close()


@pytest.fixture
def mongo_db(mongo_client):
    """An empty database on a real server, dropped afterwards."""
    name = f"hoteltrivago_{uuid.uuid4().hex[:8]}_test"
    yield mongo_client[name]
    mongo_client.drop_database(name)


@pytest.fixture
def seeded_mongo_db(mongo_db):
    """A real database with validators, indexes and the seed loaded."""
    load_seed(mongo_db, now=SEED_TIME, rounds=FAST_ROUNDS)
    return mongo_db
