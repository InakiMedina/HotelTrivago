"""The seed must match tests/data/test-data.md and the QA data files."""

import csv
from pathlib import Path

import pytest
from bson import ObjectId

from src.db import seed as seed_module
from src.db.fields import hash_password, verify_password
from src.db.seed import (
    UnsafeDatabaseError,
    check_reset_allowed,
    load_seed,
    main,
    reset_database,
)
from src.db.setup import COLLECTIONS, INDEXES

from .conftest import FAST_ROUNDS, SEED_TIME

QA_DATA = Path(__file__).resolve().parents[3] / "tests" / "data"

# tests/data/test-data.md, section 3 (prices in MXN)
EXPECTED_ROOMS = {
    "R-001": ("Standard Double", "double", {"wifi"}, 1000),
    "R-002": ("Deluxe Double", "double", {"wifi", "balcony"}, 1500),
    "R-003": ("Junior Suite", "suite", {"wifi", "minibar"}, 2000),
    "R-004": ("Master Suite", "suite", {"wifi", "balcony", "minibar"}, 2500),
    "R-005": ("Single", "single", {"wifi"}, 450),
}

# tests/data/test-data.md, section 2, plus the two staff users
EXPECTED_USERS = {
    "client1@example.com": ("Client1Pass", "user"),
    "client2@example.com": ("Client2Pass", "user"),
    "admin@example.com": ("AdminPass123", "admin"),
    "booking1@example.com": ("Booking1Pass", "booking_staff"),
    "cleaning1@example.com": ("Cleaning1Pass", "cleaning_staff"),
}


def _ids(cursor):
    return [doc["_id"] for doc in cursor]


# --- contents ---------------------------------------------------------------


def test_collections_and_counts(seeded_mock_db):
    assert set(COLLECTIONS) <= set(seeded_mock_db.list_collection_names())
    assert seeded_mock_db.users.count_documents({}) == 5
    assert seeded_mock_db.room_types.count_documents({}) == 5
    assert seeded_mock_db.room_units.count_documents({}) == 60
    assert seeded_mock_db.password_reset_tokens.count_documents({}) == 0
    assert seeded_mock_db.sessions.count_documents({}) == 0


def test_users_match_test_data(seeded_mock_db):
    users = {user["email"]: user for user in seeded_mock_db.users.find()}
    assert set(users) == set(EXPECTED_USERS)
    for email, (password, role) in EXPECTED_USERS.items():
        user = users[email]
        assert user["role"] == role
        assert user["status"] == "active"
        assert user["password_hash"].startswith("$2b$")
        assert verify_password(password, user["password_hash"])
        assert password not in user.values()


def test_user_ids_are_fixed(seeded_mock_db):
    admin = seeded_mock_db.users.find_one({"email": "admin@example.com"})
    assert admin["_id"] == ObjectId("000000000000000000000003")


def test_admin_password_can_be_overridden(mock_db, monkeypatch):
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "DemoAdmin2026")
    load_seed(mock_db, validators=False, rounds=FAST_ROUNDS)
    admin = mock_db.users.find_one({"role": "admin"})
    assert verify_password("DemoAdmin2026", admin["password_hash"])
    assert not verify_password("AdminPass123", admin["password_hash"])
    client = mock_db.users.find_one({"email": "client1@example.com"})
    assert verify_password("Client1Pass", client["password_hash"])


def test_room_types_match_test_data(seeded_mock_db):
    rooms = {room["_id"]: room for room in seeded_mock_db.room_types.find()}
    assert set(rooms) == set(EXPECTED_ROOMS)
    for room_id, (name, room_type, amenities, price_mxn) in EXPECTED_ROOMS.items():
        room = rooms[room_id]
        assert room["name"] == name
        assert room["room_type"] == room_type
        assert set(room["amenities"]) == amenities
        assert room["price_cents"] == price_mxn * 100
        assert room["active"] is True


def test_photos(seeded_mock_db):
    for room in seeded_mock_db.room_types.find():
        expected = 3 if room["_id"] == "R-002" else 1  # TC-017; TC-009 needs a photo per card
        assert len(room["photos"]) == expected


def test_upgrade_ranks_follow_the_hierarchy(seeded_mock_db):
    order = _ids(seeded_mock_db.room_types.find().sort("upgrade_rank", 1))
    assert order == ["R-005", "R-001", "R-002", "R-003", "R-004"]


def test_room_units(seeded_mock_db):
    per_type = {"R-005": 10, "R-001": 20, "R-002": 10, "R-003": 10, "R-004": 10}
    for room_type, count in per_type.items():
        assert seeded_mock_db.room_units.count_documents({"room_type_id": room_type}) == count
    floors = {"101": 1, "110": 1, "201": 2, "220": 2, "310": 3, "401": 4, "510": 5}
    for number, floor in floors.items():
        assert seeded_mock_db.room_units.find_one({"_id": number})["floor"] == floor
    assert seeded_mock_db.room_units.count_documents(
        {"occupancy": "vacant", "cleanliness": "clean", "out_of_order": False}
    ) == 60
    unit = seeded_mock_db.room_units.find_one({"_id": "301"})
    assert unit["room_type_id"] == "R-002"
    assert unit["clean_since"] == SEED_TIME


# --- the seed answers the QA queries ----------------------------------------


def test_sort_orders_of_tc_016(seeded_mock_db):
    rooms = seeded_mock_db.room_types
    assert _ids(rooms.find().sort("price_cents", 1)) == [
        "R-005", "R-001", "R-002", "R-003", "R-004"
    ]
    assert _ids(rooms.find().sort("price_cents", -1)) == [
        "R-004", "R-003", "R-002", "R-001", "R-005"
    ]


def _price_cases():
    path = QA_DATA / "price-filter.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle) if not row["expected_error"]]


@pytest.mark.parametrize("case", _price_cases(), ids=lambda row: row["case"])
def test_price_filter_cases_of_tc_014(seeded_mock_db, case):
    low, high = int(case["min_price"]) * 100, int(case["max_price"]) * 100
    found = set(_ids(seeded_mock_db.room_types.find({"price_cents": {"$gte": low, "$lte": high}})))
    expected = set(filter(None, case["expected_rooms"].split("|")))
    assert found == expected


@pytest.mark.parametrize(
    ("room_type", "amenity", "expected"),
    [
        ("suite", None, {"R-003", "R-004"}),
        ("suite", "balcony", {"R-004"}),
        (None, "balcony", {"R-002", "R-004"}),
        ("single", None, {"R-005"}),
        ("single", "balcony", set()),
    ],
)
def test_combined_filters_of_tc_015(seeded_mock_db, room_type, amenity, expected):
    query = {}
    if room_type:
        query["room_type"] = room_type
    if amenity:
        query["amenities"] = amenity
    assert set(_ids(seeded_mock_db.room_types.find(query))) == expected


# --- setup, idempotency and reset -------------------------------------------


def test_indexes_are_created(seeded_mock_db):
    for collection, indexes in INDEXES.items():
        names = set(seeded_mock_db[collection].index_information())
        assert {index.document["name"] for index in indexes} <= names


def test_load_seed_twice_inserts_nothing_new(seeded_mock_db):
    inserted = load_seed(seeded_mock_db, validators=False, rounds=FAST_ROUNDS)
    assert inserted == {"users": 0, "room_types": 0, "room_units": 0}
    assert seeded_mock_db.users.count_documents({}) == 5


def test_load_seed_keeps_changed_passwords(seeded_mock_db):
    # TC-007 changes U-02's password; seeding again must not undo it.
    new_hash = hash_password("NewPass2024", rounds=FAST_ROUNDS)
    seeded_mock_db.users.update_one(
        {"email": "client2@example.com"}, {"$set": {"password_hash": new_hash}}
    )
    load_seed(seeded_mock_db, validators=False, rounds=FAST_ROUNDS)
    user = seeded_mock_db.users.find_one({"email": "client2@example.com"})
    assert verify_password("NewPass2024", user["password_hash"])


def test_reset_restores_the_seed(seeded_mock_db):
    seeded_mock_db.users.delete_many({"role": "user"})
    seeded_mock_db.room_types.update_one({"_id": "R-001"}, {"$set": {"price_cents": 1}})
    seeded_mock_db.create_collection("leftover")
    inserted = reset_database(seeded_mock_db, validators=False, rounds=FAST_ROUNDS)
    assert inserted == {"users": 5, "room_types": 5, "room_units": 60}
    assert seeded_mock_db.room_types.find_one({"_id": "R-001"})["price_cents"] == 100000
    assert "leftover" not in seeded_mock_db.list_collection_names()


@pytest.mark.parametrize("name", ["hoteltrivago_dev", "hoteltrivago_test"])
def test_reset_allowed_for_dev_and_test(name):
    check_reset_allowed(name)


@pytest.mark.parametrize("name", ["hoteltrivago", "hoteltrivago_prod", "test_hoteltrivago"])
def test_reset_refused_for_other_names(name):
    with pytest.raises(UnsafeDatabaseError):
        check_reset_allowed(name)
    check_reset_allowed(name, force=True)


# --- command line -----------------------------------------------------------


@pytest.fixture
def cli_db(mock_db, monkeypatch):
    monkeypatch.setenv("BCRYPT_ROUNDS", str(FAST_ROUNDS))
    monkeypatch.setattr(seed_module, "get_db", lambda: mock_db)
    monkeypatch.setattr(seed_module, "setup_database", _setup_without_validators)
    return mock_db


def _setup_without_validators(db, **_options):  # mongomock has no validators
    from src.db.setup import setup_database

    setup_database(db, validators=False)


def test_cli_seed(cli_db, capsys):
    assert main([]) == 0
    assert "inserted users: 5, password_reset_tokens: 0" in capsys.readouterr().out
    assert cli_db.room_units.count_documents({}) == 60


def test_cli_reset(cli_db, capsys):
    main([])
    cli_db.users.delete_many({})
    assert main(["--reset"]) == 0
    assert "reset and seeded" in capsys.readouterr().out
    assert cli_db.users.count_documents({}) == 5


def test_cli_reset_refuses_unsafe_database(mock_db, monkeypatch, capsys):
    unsafe = mock_db.client["hoteltrivago"]
    monkeypatch.setattr(seed_module, "get_db", lambda: unsafe)
    assert main(["--reset"]) == 2
    assert "refusing to reset 'hoteltrivago'" in capsys.readouterr().err
