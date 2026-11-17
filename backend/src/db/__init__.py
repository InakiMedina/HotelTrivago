"""MongoDB layer: connection, collection schemas, indexes and seed data.

See ``docs/database/schema.md`` for the collections and their fields.
"""

from .client import close_client, get_client, get_db
from .fields import hash_password, hash_token, normalize_email, verify_password
from .setup import COLLECTIONS, setup_database

__all__ = [
    "COLLECTIONS",
    "close_client",
    "get_client",
    "get_db",
    "hash_password",
    "hash_token",
    "normalize_email",
    "setup_database",
    "verify_password",
]
