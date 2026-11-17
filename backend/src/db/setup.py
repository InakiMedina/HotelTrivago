"""Collections, validators and indexes.

``setup_database(db)`` creates every collection with its ``$jsonSchema``
validator and builds its indexes. It is safe to run on an existing database:
missing collections are created, existing ones get the current validator, and
indexes that already exist are left alone.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pymongo import ASCENDING, IndexModel
from pymongo.database import Database

SCHEMA_DIR = Path(__file__).parent / "schemas"

COLLECTIONS: tuple[str, ...] = (
    "users",
    "password_reset_tokens",
    "sessions",
    "room_types",
    "room_units",
)

# A reset token stays one day after it expires so QA can inspect it; the API
# must always check expires_at itself, because MongoDB only removes expired
# documents about once a minute.
RESET_TOKEN_TTL_SECONDS = 24 * 60 * 60

INDEXES: dict[str, list[IndexModel]] = {
    "users": [
        IndexModel([("email", ASCENDING)], name="email_unique", unique=True),
        IndexModel([("role", ASCENDING), ("status", ASCENDING)], name="role_status"),
    ],
    "password_reset_tokens": [
        IndexModel([("token_hash", ASCENDING)], name="token_hash_unique", unique=True),
        IndexModel([("user_id", ASCENDING), ("status", ASCENDING)], name="user_status"),
        IndexModel(
            [("expires_at", ASCENDING)],
            name="expires_at_ttl",
            expireAfterSeconds=RESET_TOKEN_TTL_SECONDS,
        ),
    ],
    "sessions": [
        IndexModel([("token_id", ASCENDING)], name="token_id_unique", unique=True),
        IndexModel([("user_id", ASCENDING)], name="user_id"),
        IndexModel([("expires_at", ASCENDING)], name="expires_at_ttl", expireAfterSeconds=0),
    ],
    "room_types": [
        IndexModel(
            [("upgrade_rank", ASCENDING)],
            name="upgrade_rank_unique",
            unique=True,
            partialFilterExpression={"upgrade_rank": {"$type": "number"}},
        ),
    ],
    "room_units": [
        IndexModel(
            [("room_type_id", ASCENDING), ("occupancy", ASCENDING), ("cleanliness", ASCENDING)],
            name="type_occupancy_cleanliness",
        ),
    ],
}


@lru_cache(maxsize=None)
def _schema_text(collection: str) -> str:
    return (SCHEMA_DIR / f"{collection}.json").read_text(encoding="utf-8")


def load_schema(collection: str) -> dict:
    """Return the validator document for ``collection`` (a fresh copy)."""
    return json.loads(_schema_text(collection))


def ensure_collections(db: Database, *, validators: bool = True) -> None:
    """Create the collections and apply their validators.

    ``validators=False`` skips the validators; use it only with mongomock,
    which does not support them.
    """
    existing = set(db.list_collection_names())
    for name in COLLECTIONS:
        if not validators:
            if name not in existing:
                db.create_collection(name)
            continue
        options = {
            "validator": load_schema(name),
            "validationLevel": "strict",
            "validationAction": "error",
        }
        if name in existing:
            db.command({"collMod": name, **options})
        else:
            db.create_collection(name, **options)


def ensure_indexes(db: Database) -> None:
    """Build every index in ``INDEXES``; existing ones are kept."""
    for name, indexes in INDEXES.items():
        db[name].create_indexes(indexes)


def setup_database(db: Database, *, validators: bool = True) -> None:
    """Create collections, validators and indexes."""
    ensure_collections(db, validators=validators)
    ensure_indexes(db)
