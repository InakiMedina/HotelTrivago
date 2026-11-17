"""MongoDB connection.

The backend gets the database with ``get_db()``. The connection is configured
with environment variables:

- ``MONGO_URI``: server address (default ``mongodb://localhost:27017``).
- ``MONGO_DB_NAME``: database name (default ``hoteltrivago_dev``).
- ``MONGO_TIMEOUT_MS``: how long to wait for the server before failing
  (default 5000), so a stopped database gives a quick error (TC-021)
  instead of hanging for 30 seconds.
"""

from __future__ import annotations

import os

from pymongo import MongoClient
from pymongo.database import Database

DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB_NAME = "hoteltrivago_dev"
DEFAULT_TIMEOUT_MS = 5000

_client: MongoClient | None = None  # pylint: disable=invalid-name


def mongo_uri() -> str:
    """Server address from ``MONGO_URI``."""
    return os.environ.get("MONGO_URI", DEFAULT_URI)


def db_name() -> str:
    """Database name from ``MONGO_DB_NAME``."""
    return os.environ.get("MONGO_DB_NAME", DEFAULT_DB_NAME)


def timeout_ms() -> int:
    """Server selection timeout from ``MONGO_TIMEOUT_MS``."""
    return int(os.environ.get("MONGO_TIMEOUT_MS", DEFAULT_TIMEOUT_MS))


def get_client() -> MongoClient:
    """Return the shared client, creating it on first use.

    ``tz_aware=True`` makes every date read from MongoDB a timezone-aware UTC
    ``datetime``, so it compares safely with ``datetime.now(timezone.utc)``.
    """
    global _client  # pylint: disable=global-statement
    if _client is None:
        _client = MongoClient(
            mongo_uri(),
            tz_aware=True,
            serverSelectionTimeoutMS=timeout_ms(),
            appname="hoteltrivago-backend",
        )
    return _client


def get_db(name: str | None = None) -> Database:
    """Return the application database (or ``name`` when given)."""
    return get_client()[name or db_name()]


def close_client() -> None:
    """Close the shared client; the next ``get_client()`` opens a new one."""
    global _client  # pylint: disable=global-statement
    if _client is not None:
        _client.close()
        _client = None
