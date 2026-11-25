import re

import pytest

from src.db.fields import (
    bcrypt_rounds,
    hash_password,
    hash_token,
    normalize_email,
    verify_password,
)
from src.db.setup import load_schema


def _pattern(collection, field):
    return load_schema(collection)["$jsonSchema"]["properties"][field]["pattern"]


def test_normalize_email_trims_and_lowercases():
    assert normalize_email("  CLIENT1@Example.com ") == "client1@example.com"


def test_hash_password_matches_users_schema():
    hashed = hash_password("Client1Pass", rounds=4)
    assert hashed.startswith("$2b$04$")
    assert len(hashed) == 60
    assert re.fullmatch(_pattern("users", "password_hash"), hashed)


def test_verify_password():
    hashed = hash_password("Client1Pass", rounds=4)
    assert verify_password("Client1Pass", hashed)
    assert not verify_password("client1pass", hashed)
    assert not verify_password("Client1Pass", "not-a-bcrypt-hash")


def test_password_of_64_characters_is_accepted():
    password = "A" * 63 + "1"  # BR-01 maximum
    assert verify_password(password, hash_password(password, rounds=4))


def test_password_over_72_bytes_is_rejected():
    long_password = "ñ" * 40  # 40 characters, 80 bytes
    with pytest.raises(ValueError):
        hash_password(long_password, rounds=4)
    assert not verify_password(long_password, hash_password("short1", rounds=4))


def test_bcrypt_rounds_from_environment(monkeypatch):
    monkeypatch.delenv("BCRYPT_ROUNDS", raising=False)
    assert bcrypt_rounds() == 12
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")
    assert bcrypt_rounds() == 4
    assert hash_password("Client1Pass").startswith("$2b$04$")
    monkeypatch.setenv("BCRYPT_ROUNDS", "3")
    with pytest.raises(ValueError):
        bcrypt_rounds()


def test_hash_token_matches_schema():
    digest = hash_token("raw-token-from-the-email")
    assert digest == hash_token("raw-token-from-the-email")
    assert digest != hash_token("another-token")
    assert re.fullmatch(_pattern("password_reset_tokens", "token_hash"), digest)
