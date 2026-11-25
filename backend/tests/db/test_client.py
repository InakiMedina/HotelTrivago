import pytest

from src.db import client as db_client


@pytest.fixture(autouse=True)
def fresh_client():
    db_client.close_client()
    yield
    db_client.close_client()


def test_defaults(monkeypatch):
    for name in ("MONGO_URI", "MONGO_DB_NAME", "MONGO_TIMEOUT_MS"):
        monkeypatch.delenv(name, raising=False)
    assert db_client.mongo_uri() == "mongodb://localhost:27017"
    assert db_client.db_name() == "hoteltrivago_dev"
    assert db_client.timeout_ms() == 5000


def test_get_db_reads_the_environment(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://mongo:27017")
    monkeypatch.setenv("MONGO_DB_NAME", "hoteltrivago_test")
    monkeypatch.setenv("MONGO_TIMEOUT_MS", "1000")
    db = db_client.get_db()
    assert db.name == "hoteltrivago_test"
    assert db.client.options.server_selection_timeout == 1.0
    assert db.client.codec_options.tz_aware is True
    assert db_client.get_db("other_test").name == "other_test"


def test_client_is_shared_until_closed(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://mongo:27017")
    first = db_client.get_client()
    assert db_client.get_client() is first
    db_client.close_client()
    assert db_client.get_client() is not first
