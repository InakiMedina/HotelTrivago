"""Validators and indexes on a real MongoDB (mongomock ignores both)."""

from datetime import datetime, timedelta, timezone

import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, WriteError

from src.db.fields import hash_password, hash_token
from src.db.seed import load_seed, reset_database
from src.db.setup import COLLECTIONS, INDEXES, load_schema, setup_database

from .conftest import FAST_ROUNDS

pytestmark = pytest.mark.mongo

NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
HASH = hash_password("ValidPass123", rounds=FAST_ROUNDS)


def user(**changes):
    doc = {
        "_id": ObjectId(),
        "email": "newuser@example.com",
        "password_hash": HASH,
        "role": "user",
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    }
    doc.update(changes)
    return doc


def token(**changes):
    doc = {
        "_id": ObjectId(),
        "user_id": ObjectId("000000000000000000000002"),
        "token_hash": hash_token(str(ObjectId())),
        "status": "issued",
        "created_at": NOW,
        "expires_at": NOW + timedelta(minutes=10),
    }
    doc.update(changes)
    return doc


def session(**changes):
    doc = {
        "_id": ObjectId(),
        "token_id": "6f1d2c3b-4a5e-4f60-8a7b-9c0d1e2f3a4b",
        "user_id": ObjectId("000000000000000000000001"),
        "created_at": NOW,
        "expires_at": NOW + timedelta(hours=1),
    }
    doc.update(changes)
    return doc


def room_type(**changes):
    # The room TC-018 (a) creates: name, type, price and one photo.
    doc = {
        "_id": "R-006",
        "name": "QA Test Room",
        "room_type": "double",
        "price_cents": 120000,
        "amenities": [],
        "photos": [{"url": "/media/rooms/qa-test-room.jpg"}],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    }
    doc.update(changes)
    return doc


def room_unit(**changes):
    doc = {
        "_id": "999",
        "floor": 9,
        "room_type_id": "R-001",
        "occupancy": "vacant",
        "cleanliness": "clean",
        "out_of_order": False,
        "updated_at": NOW,
    }
    doc.update(changes)
    return doc


def card(**changes):
    # Never a full card number or a CVV, not even in tests.
    doc = {
        "_id": ObjectId(),
        "user_id": ObjectId("000000000000000000000004"),
        "holder_name": "Booking Staff One",
        "brand": "visa",
        "last4": "0004",
        "exp_month": 12,
        "exp_year": 2030,
        "created_at": NOW,
        "updated_at": NOW,
    }
    doc.update(changes)
    return doc


PHONE = {"country_code": "+52", "number": "5500000009"}


def without(doc, field):
    doc.pop(field)
    return doc


VALID = [
    ("users", user()),
    ("users", user(role="cleaning_staff", status="terminated")),
    ("users", user(first_name="María José", last_name="Pérez de la Rosa", phone=PHONE)),
    ("users", user(first_name=None, last_name=None, phone=None)),
    ("users", user(phone={"country_code": "+1", "number": "2025550100"})),
    ("password_reset_tokens", token()),
    ("password_reset_tokens", token(status="used", used_at=NOW)),
    ("password_reset_tokens", token(status="superseded", superseded_at=NOW)),
    ("sessions", session()),
    ("room_types", room_type()),
    ("room_types", room_type(description="<script>alert('xss')</script> Quiet room")),
    ("room_types", room_type(upgrade_rank=None, max_guests=10)),
    ("room_units", room_unit()),
    ("room_units", room_unit(occupancy="occupied", cleanliness="dirty")),
    ("room_units", room_unit(occupancy="occupied", cleanliness="cleaning")),
    ("room_units", room_unit(cleanliness="dirty", clean_since=None, current_booking_id=None)),
    ("payment_cards", card()),
    ("payment_cards", card(brand="amex", exp_month=1, exp_year=2031)),
]

INVALID = {
    "email with capitals (BR-07)": ("users", user(email="NewUser@Example.com")),
    "email without domain": ("users", user(email="user@")),
    "email with spaces": ("users", user(email="user name@example.com")),
    "plain-text password (TC-001)": ("users", user(password_hash="ValidPass123")),
    "unknown role": ("users", user(role="manager")),
    "unknown status": ("users", user(status="deleted")),
    "missing status": ("users", without(user(), "status")),
    "unknown field": ("users", user(password="ValidPass123")),
    "date as text": ("users", user(created_at="2026-11-17")),
    "full_name was replaced": ("users", user(full_name="New User")),
    "empty first name": ("users", user(first_name="")),
    "blank last name": ("users", user(last_name="   ")),
    "first name too long": ("users", user(first_name="a" * 61)),
    "phone as text": ("users", user(phone="+525500000009")),
    "phone without number": ("users", user(phone={"country_code": "+52"})),
    "phone without country code": ("users", user(phone={"number": "5500000009"})),
    "country code without plus": ("users", user(phone={**PHONE, "country_code": "52"})),
    "phone with letters": ("users", user(phone={**PHONE, "number": "55-0000-0009"})),
    "phone too short": ("users", user(phone={**PHONE, "number": "123"})),
    "phone with extra field": ("users", user(phone={**PHONE, "ext": "12"})),
    "used token without used_at": ("password_reset_tokens", token(status="used")),
    "superseded token without date": ("password_reset_tokens", token(status="superseded")),
    "raw token stored": ("password_reset_tokens", token(token_hash="raw-token")),
    "unknown token status": ("password_reset_tokens", token(status="expired")),
    "session without expiry": ("sessions", without(session(), "expires_at")),
    "short session token id": ("sessions", session(token_id="abc")),
    "price of zero (TC-018 d)": ("room_types", room_type(price_cents=0)),
    "negative price (TC-018 d)": ("room_types", room_type(price_cents=-100)),
    "price as decimal": ("room_types", room_type(price_cents=1200.5)),
    "missing name (TC-018 b)": ("room_types", without(room_type(), "name")),
    "blank name": ("room_types", room_type(name="   ")),
    "missing room type (TC-018 c)": ("room_types", without(room_type(), "room_type")),
    "unknown room type": ("room_types", room_type(room_type="penthouse")),
    "unknown amenity": ("room_types", room_type(amenities=["pool"])),
    "repeated amenity": ("room_types", room_type(amenities=["wifi", "wifi"])),
    "malformed id": ("room_types", room_type(_id="abc")),
    "photo without url": ("room_types", room_type(photos=[{"alt": "no url"}])),
    "too many guests": ("room_types", room_type(max_guests=11)),
    "occupied and clean (BR-33)": ("room_units", room_unit(occupancy="occupied")),
    "unknown cleanliness": ("room_units", room_unit(cleanliness="cleaned")),
    "room number as int": ("room_units", room_unit(_id=999)),
    "card number field": ("payment_cards", card(card_number=None)),
    "cvv field": ("payment_cards", card(cvv=None)),
    "more than 4 digits": ("payment_cards", card(last4="00004")),
    "last4 with letters": ("payment_cards", card(last4="abcd")),
    "unknown brand": ("payment_cards", card(brand="discover")),
    "month 13": ("payment_cards", card(exp_month=13)),
    "month 0": ("payment_cards", card(exp_month=0)),
    "year as text": ("payment_cards", card(exp_year="2030")),
    "blank holder name": ("payment_cards", card(holder_name=" ")),
    "card without owner": ("payment_cards", without(card(), "user_id")),
}


def test_every_collection_has_a_strict_validator(seeded_mongo_db):
    for name in COLLECTIONS:
        options = seeded_mongo_db[name].options()
        assert options["validator"] == load_schema(name)
        assert options["validationLevel"] == "strict"
        assert options["validationAction"] == "error"


def test_seed_passes_the_validators(seeded_mongo_db):
    assert seeded_mongo_db.users.count_documents({}) == 5
    assert seeded_mongo_db.room_types.count_documents({}) == 5
    assert seeded_mongo_db.room_units.count_documents({}) == 60
    assert seeded_mongo_db.payment_cards.count_documents({}) == 2


@pytest.mark.parametrize(("collection", "doc"), VALID)
def test_valid_documents_are_accepted(seeded_mongo_db, collection, doc):
    seeded_mongo_db[collection].insert_one(doc)


@pytest.mark.parametrize(("collection", "doc"), INVALID.values(), ids=INVALID.keys())
def test_invalid_documents_are_rejected(seeded_mongo_db, collection, doc):
    with pytest.raises(WriteError) as error:
        seeded_mongo_db[collection].insert_one(doc)
    assert error.value.code == 121  # DocumentValidationFailure


def test_updates_are_validated_too(seeded_mongo_db):
    with pytest.raises(WriteError):
        seeded_mongo_db.room_units.update_one(
            {"_id": "101"}, {"$set": {"occupancy": "occupied"}}
        )  # would leave an occupied room clean
    seeded_mongo_db.room_units.update_one(
        {"_id": "101"}, {"$set": {"occupancy": "occupied", "cleanliness": "dirty"}}
    )


def test_duplicate_email_is_rejected(seeded_mongo_db):
    with pytest.raises(DuplicateKeyError):
        seeded_mongo_db.users.insert_one(user(email="client1@example.com"))


def test_duplicate_token_hash_is_rejected(seeded_mongo_db):
    first = token()
    seeded_mongo_db.password_reset_tokens.insert_one(first)
    with pytest.raises(DuplicateKeyError):
        seeded_mongo_db.password_reset_tokens.insert_one(token(token_hash=first["token_hash"]))


def test_duplicate_session_token_is_rejected(seeded_mongo_db):
    seeded_mongo_db.sessions.insert_one(session())
    with pytest.raises(DuplicateKeyError):
        seeded_mongo_db.sessions.insert_one(session())


def test_upgrade_rank_is_unique_only_when_set(seeded_mongo_db):
    with pytest.raises(DuplicateKeyError):
        seeded_mongo_db.room_types.insert_one(room_type(upgrade_rank=1))
    seeded_mongo_db.room_types.insert_one(room_type(_id="R-006"))
    seeded_mongo_db.room_types.insert_one(room_type(_id="R-007", upgrade_rank=None))


def test_indexes(seeded_mongo_db):
    for collection, indexes in INDEXES.items():
        info = seeded_mongo_db[collection].index_information()
        for index in indexes:
            assert index.document["name"] in info
    resets = seeded_mongo_db.password_reset_tokens.index_information()
    assert resets["expires_at_ttl"]["expireAfterSeconds"] == 24 * 60 * 60
    sessions = seeded_mongo_db.sessions.index_information()
    assert sessions["expires_at_ttl"]["expireAfterSeconds"] == 0
    assert seeded_mongo_db.users.index_information()["email_unique"]["unique"] is True


def test_setup_adds_validators_to_existing_collections(mongo_db):
    mongo_db.create_collection("users")
    setup_database(mongo_db)
    assert mongo_db.users.options()["validator"] == load_schema("users")
    setup_database(mongo_db)  # running it again changes nothing


def test_reset_on_a_real_server(seeded_mongo_db):
    seeded_mongo_db.users.delete_many({})
    inserted = reset_database(seeded_mongo_db, rounds=FAST_ROUNDS)
    assert inserted == {"users": 5, "room_types": 5, "room_units": 60, "payment_cards": 2}
    assert load_seed(seeded_mongo_db, rounds=FAST_ROUNDS) == {
        "users": 0,
        "room_types": 0,
        "room_units": 0,
        "payment_cards": 0,
    }
