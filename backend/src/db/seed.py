"""Seed data and database reset.

Command line (run from ``backend/``)::

    python -m src.db.seed            # create what is missing, never deletes
    python -m src.db.seed --reset    # drop the database and load the seed again

``--reset`` only runs on a database whose name ends in ``_dev`` or ``_test``,
unless ``--force`` is given, so nobody wipes the demo database by accident.

The seed matches ``tests/data/test-data.md``: users U-01 to U-03 (plus the
staff users U-04 and U-05), rooms R-001 to R-005 and the 60 physical rooms.
``SEED_ADMIN_PASSWORD`` replaces the admin password, for deployed demos.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from pymongo.database import Database

from .client import get_db
from .fields import hash_password, normalize_email
from .setup import COLLECTIONS, setup_database

SEED_DIR = Path(__file__).parent / "seed_data"
SAFE_DB_SUFFIXES = ("_dev", "_test")


class UnsafeDatabaseError(RuntimeError):
    """Raised when a reset targets a database that is not for dev or tests."""


def _read(name: str) -> list[dict]:
    return json.loads((SEED_DIR / f"{name}.json").read_text(encoding="utf-8"))


def build_users(
    now: datetime, *, rounds: int | None = None, admin_password: str | None = None
) -> list[dict]:
    """Seed users with hashed passwords."""
    admin_password = admin_password or os.environ.get("SEED_ADMIN_PASSWORD")
    users = []
    for entry in _read("users"):
        password = entry["password"]
        if entry["role"] == "admin" and admin_password:
            password = admin_password
        users.append(
            {
                "_id": ObjectId(entry["_id"]),
                "email": normalize_email(entry["email"]),
                "password_hash": hash_password(password, rounds=rounds),
                "role": entry["role"],
                "status": "active",
                "full_name": entry["full_name"],
                "created_at": now,
                "updated_at": now,
            }
        )
    return users


def build_room_types(now: datetime) -> list[dict]:
    """Seed room categories R-001 to R-005."""
    return [
        {**entry, "active": True, "created_at": now, "updated_at": now}
        for entry in _read("room_types")
    ]


def build_room_units(now: datetime) -> list[dict]:
    """Seed physical rooms, all vacant and clean."""
    units = []
    for block in _read("room_units"):
        for number in range(block["first"], block["last"] + 1):
            units.append(
                {
                    "_id": str(number),
                    "floor": block["floor"],
                    "room_type_id": block["room_type_id"],
                    "occupancy": "vacant",
                    "cleanliness": "clean",
                    "out_of_order": False,
                    "clean_since": now,
                    "updated_at": now,
                }
            )
    return units


def seed_documents(
    now: datetime | None = None,
    *,
    rounds: int | None = None,
    admin_password: str | None = None,
) -> dict[str, list[dict]]:
    """Every seed document, by collection."""
    now = now or datetime.now(timezone.utc)
    return {
        "users": build_users(now, rounds=rounds, admin_password=admin_password),
        "room_types": build_room_types(now),
        "room_units": build_room_units(now),
    }


def load_seed(
    db: Database,
    *,
    validators: bool = True,
    now: datetime | None = None,
    rounds: int | None = None,
    admin_password: str | None = None,
) -> dict[str, int]:
    """Set up the database and insert the seed documents that are missing.

    Existing documents are never changed, so a password changed during a test
    (TC-007) survives. Returns how many documents were inserted per collection.
    """
    setup_database(db, validators=validators)
    inserted = {}
    docs = seed_documents(now, rounds=rounds, admin_password=admin_password)
    for collection, items in docs.items():
        count = 0
        for doc in items:
            fields = {key: value for key, value in doc.items() if key != "_id"}
            result = db[collection].update_one(
                {"_id": doc["_id"]}, {"$setOnInsert": fields}, upsert=True
            )
            if result.upserted_id is not None:
                count += 1
        inserted[collection] = count
    return inserted


def check_reset_allowed(db_name: str, *, force: bool = False) -> None:
    """Refuse to reset a database whose name does not end in _dev or _test."""
    if not force and not db_name.endswith(SAFE_DB_SUFFIXES):
        raise UnsafeDatabaseError(
            f"refusing to reset '{db_name}': the name does not end in "
            f"{' or '.join(SAFE_DB_SUFFIXES)}; use --force if you are sure"
        )


def reset_database(  # pylint: disable=too-many-arguments
    db: Database,
    *,
    force: bool = False,
    validators: bool = True,
    now: datetime | None = None,
    rounds: int | None = None,
    admin_password: str | None = None,
) -> dict[str, int]:
    """Drop the whole database and load the seed again."""
    check_reset_allowed(db.name, force=force)
    db.client.drop_database(db.name)
    return load_seed(
        db, validators=validators, now=now, rounds=rounds, admin_password=admin_password
    )


def main(argv: list[str] | None = None) -> int:
    """Command line entry point."""
    parser = argparse.ArgumentParser(
        prog="python -m src.db.seed",
        description="Create the HotelTrivago collections and load the seed data.",
    )
    parser.add_argument(
        "--reset", action="store_true", help="drop the database first (dev and test only)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow --reset on a database whose name does not end in _dev or _test",
    )
    args = parser.parse_args(argv)

    db = get_db()
    try:
        if args.reset:
            inserted = reset_database(db, force=args.force)
        else:
            inserted = load_seed(db)
    except UnsafeDatabaseError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    action = "reset and seeded" if args.reset else "seeded"
    summary = ", ".join(f"{name}: {inserted.get(name, 0)}" for name in COLLECTIONS)
    print(f"{db.name} {action} (inserted {summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
