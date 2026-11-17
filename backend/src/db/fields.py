"""Helpers that produce values in the exact format the schemas require.

The seed uses them, and the backend should use them too, so that what the API
writes always matches what the validators accept.
"""

from __future__ import annotations

import hashlib
import os

import bcrypt

DEFAULT_BCRYPT_ROUNDS = 12
# bcrypt only reads the first 72 bytes of a password. BR-01 allows up to 64
# characters, but non-ASCII characters take more than one byte, so the limit is
# checked explicitly instead of letting bcrypt truncate (4.x) or fail (5.x).
BCRYPT_MAX_BYTES = 72


def normalize_email(email: str) -> str:
    """Return the stored form of an email: trimmed and lowercase (BR-07)."""
    return email.strip().lower()


def bcrypt_rounds() -> int:
    """Cost factor from ``BCRYPT_ROUNDS`` (default 12; use 4 in tests)."""
    rounds = int(os.environ.get("BCRYPT_ROUNDS", DEFAULT_BCRYPT_ROUNDS))
    if not 4 <= rounds <= 31:
        raise ValueError(f"BCRYPT_ROUNDS must be between 4 and 31, got {rounds}")
    return rounds


def hash_password(password: str, rounds: int | None = None) -> str:
    """Return a bcrypt ``$2b$`` hash of ``password`` (60 characters)."""
    raw = password.encode("utf-8")
    if len(raw) > BCRYPT_MAX_BYTES:
        raise ValueError(f"password is longer than {BCRYPT_MAX_BYTES} bytes")
    salt = bcrypt.gensalt(rounds=rounds or bcrypt_rounds())
    return bcrypt.hashpw(raw, salt).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Return True when ``password`` matches ``password_hash``."""
    raw = password.encode("utf-8")
    if len(raw) > BCRYPT_MAX_BYTES:
        return False
    try:
        return bcrypt.checkpw(raw, password_hash.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        return False


def hash_token(raw_token: str) -> str:
    """Return the SHA-256 hex digest stored for a reset or session token.

    Only the hash is stored; the raw token travels in the email link or the
    auth header, so a copy of the database cannot be used to log in.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
