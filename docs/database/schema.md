# Database Schema — Phase 1

**Owner**: Angel Isaac Barbarin Cuevas (DB Lead)
**Scope**: authentication and room catalog (FR-1 to FR-7, FR-14) — everything the M3 test cases (TC-001 to TC-023) need.
**Code**: [`backend/src/db/`](../../backend/src/db/)

Phase 1 has 5 collections. Reservations, payments, staff and payroll (phase 2) are not included yet: they depend on open questions about the architecture docs.

---

## 1. Conventions

| Topic | Rule | Example |
| --- | --- | --- |
| Names | English, `snake_case`; collections in plural | `room_types.price_cents` |
| Catalog `_id` | Readable natural key | `"R-002"`, `"301"` |
| Other `_id` | ObjectId; the API sends it as a 24-character string | `users`, `sessions` |
| Money | Integer MXN cents, taxes included; the API shows pesos | 1,500 MXN → `150000` |
| Instants | BSON Date in UTC (the client is `tz_aware`) | `created_at`, `expires_at` |
| Closed lists | Lowercase codes; the frontend shows the label | `wifi` → "Wi-Fi", `suite` → "Suite" |
| Text | Stored as typed; the frontend escapes it on display | TC-022 c, d |
| Deletion | Logical for room types (`active: false`) | TC-018 step 5 |

---

## 2. Collections

### `users`

One collection for clients, staff and admins: everyone logs in the same way and the role decides the portal.

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `_id` | ObjectId | Fixed in the seed for the test users | test-data |
| `email` | string | Trimmed and lowercase; unique | BR-07, TC-004 |
| `password_hash` | string | bcrypt `$2b$`, 60 characters; never the password | BR-01, TC-001 step 5 |
| `role` | enum | `user`, `booking_staff`, `cleaning_staff`, `admin` | RBAC, TC-019 |
| `status` | enum | `active`, `terminated`; `terminated` cannot log in | — |
| `full_name` | string, optional | Header and "My account" | TC-005 step 1 |
| `created_at`, `updated_at` | date | — | — |

### `password_reset_tokens`

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `_id` | ObjectId | — | — |
| `user_id` | ObjectId → `users` | — | — |
| `token_hash` | string | SHA-256 of the token (`hash_token()`); the raw token only goes in the email; unique | BR-06 |
| `status` | enum | `issued`, `used`, `superseded` | ST-1 |
| `created_at` | date | QA edits it directly to simulate expiry | TC-008 |
| `expires_at` | date | `created_at` + 10 minutes | BR-06 |
| `used_at` | date | Required when `status` is `used` | ST-1, TC-023 |
| `superseded_at` | date | Required when `status` is `superseded` | ST-1 |

- A token is **expired** when `status` is `issued` and `expires_at` is in the past. There is no `expired` status: it depends on the clock.
- Requesting a new token first sets every `issued` token of that user to `superseded` (BR-06).
- An unknown email creates nothing, and the response is the same (BR-08).

### `sessions`

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `_id` | ObjectId | — | — |
| `token_id` | string | JWT `jti`, or `hash_token()` of an opaque token; unique | TC-005 |
| `user_id` | ObjectId → `users` | — | — |
| `created_at` | date | — | — |
| `expires_at` | date | Session lifetime (short in the test configuration) | TC-005 step 7 |

A session is valid while its document exists **and** `expires_at` is in the future. Logout deletes the document; firing someone deletes all their sessions. Because sessions live in MongoDB, they survive a backend restart (TC-023).

### `room_types`

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `_id` | string | `R-###`; the admin creates the next free one | test-data, TC-017 |
| `name` | string | Required, 1–80 characters, not blank | TC-018 b |
| `room_type` | enum | `single`, `double`, `suite` | TC-015, TC-018 c |
| `description` | string, optional | Up to 2,000 characters | FR-7 |
| `price_cents` | int | Greater than 0 | TC-018 d, BR-05 |
| `amenities` | array | No repeats; `wifi`, `balcony`, `minibar` | TC-015 |
| `photos` | array | `{url, alt?}`, up to 20; R-002 has 3 | TC-017 |
| `max_guests` | int, optional | 1–10 | — |
| `bed_configuration` | string, optional | — | — |
| `upgrade_rank` | int, optional | 1 = lowest tier; unique when set | Collision upgrades |
| `active` | bool | `false` = deleted: hidden from search, detail returns 404 | TC-018 step 5 |
| `created_at`, `updated_at` | date | — | — |

With string ids, the TC-017 ids `000000000000000000000000` and `abc` simply do not exist, so the API can answer 404 without errors.

### `room_units`

The 60 physical rooms. No M3 test case uses them yet, but the overbooking capacity (N) is the number of units per type.

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `_id` | string | Room number, `"101"` to `"510"` | — |
| `floor` | int | ≥ 1 | — |
| `room_type_id` | string → `room_types` | — | — |
| `occupancy` | enum | `vacant`, `occupied` | BR-33 |
| `cleanliness` | enum | `clean`, `dirty`, `cleaning`; an `occupied` room is never `clean` | BR-33 |
| `out_of_order` | bool | Not counted in N, never assigned | — |
| `clean_since` | date or null | When it last became clean (for BR-34) | BR-34 |
| `current_booking_id` | ObjectId or null | Phase 2 | BR-11 |
| `updated_at` | date | — | — |

---

## 3. Indexes

| Collection | Index | Type | Used by |
| --- | --- | --- | --- |
| `users` | `email_unique` `{email: 1}` | Unique | Login, registration, duplicate email (TC-004) |
| `users` | `role_status` `{role: 1, status: 1}` | Normal | Staff lists |
| `password_reset_tokens` | `token_hash_unique` `{token_hash: 1}` | Unique | Opening the email link (TC-007) |
| `password_reset_tokens` | `user_status` `{user_id: 1, status: 1}` | Normal | Superseding older tokens (BR-06) |
| `password_reset_tokens` | `expires_at_ttl` `{expires_at: 1}` | TTL, 1 day after expiry | Cleanup |
| `sessions` | `token_id_unique` `{token_id: 1}` | Unique | Checking every authenticated request |
| `sessions` | `user_id` `{user_id: 1}` | Normal | Ending all sessions of a user |
| `sessions` | `expires_at_ttl` `{expires_at: 1}` | TTL, at expiry | Cleanup |
| `room_types` | `upgrade_rank_unique` `{upgrade_rank: 1}` | Unique, partial | Upgrade order without ties |
| `room_units` | `type_occupancy_cleanliness` | Normal | Assignable rooms of a type; counting N |

MongoDB removes expired documents about once a minute, so **the API must always compare `expires_at` with the current time** and never rely on the document being gone (TC-005 step 7, TC-008).

---

## 4. Validation

MongoDB checks the shape of every insert and update (`$jsonSchema`, `validationLevel: strict`, `validationAction: error`, `additionalProperties: false`). The schemas are in [`backend/src/db/schemas/`](../../backend/src/db/schemas/); a new field means a PR to that file.

| What | Where | Example |
| --- | --- | --- |
| Types, required fields, enums, patterns | MongoDB | A role outside the list is rejected |
| Simple ranges | MongoDB | `price_cents` > 0 |
| Combinations in one document | MongoDB (`anyOf`) | Occupied and clean is rejected (BR-33) |
| Uniqueness | MongoDB (unique indexes) | Duplicate email |
| Rules about dates or other documents | Backend | BR-02, BR-03, BR-04 |
| Password policy | Backend, before hashing | BR-01 |
| User-facing error messages | Backend | `invalid_email_format`, "Name is required" |
| NoSQL injection | Backend: reject an object where text is expected | TC-022 a, b |
| HTML escaping | Frontend, on display | TC-022 c, d |

A MongoDB validation error that reaches the user is a backend bug (it would be a 500): the backend validates first and MongoDB is the last line of defense.

---

## 5. Seed and reset

The seed matches [`tests/data/test-data.md`](../../tests/data/test-data.md), plus two staff users that are not in that file yet.

| ID | Email | Password | Role | `_id` |
| --- | --- | --- | --- | --- |
| U-01 | `client1@example.com` | `Client1Pass` | `user` | `000000000000000000000001` |
| U-02 | `client2@example.com` | `Client2Pass` | `user` | `000000000000000000000002` |
| U-03 | `admin@example.com` | `AdminPass123` | `admin` | `000000000000000000000003` |
| U-04 | `booking1@example.com` | `Booking1Pass` | `booking_staff` | `000000000000000000000004` |
| U-05 | `cleaning1@example.com` | `Cleaning1Pass` | `cleaning_staff` | `000000000000000000000005` |

It also loads R-001 to R-005 (R-002 with 3 photos, the others with 1) and the 60 physical rooms, all vacant and clean: 101–110 Single, 201–220 Standard Double, 301–310 Deluxe Double, 401–410 Junior Suite, 501–510 Master Suite. The data files are in [`backend/src/db/seed_data/`](../../backend/src/db/seed_data/).

Commands, run from `backend/`:

```bash
python -m src.db.seed            # creates collections, validators, indexes and missing seed documents; never deletes
python -m src.db.seed --reset    # drops the database and loads the seed again
```

- `--reset` only runs on a database whose name ends in `_dev` or `_test`; any other name needs `--force`.
- Without `--reset`, existing documents are never changed, so a password changed in a test (TC-007) survives.
- Tests can call `load_seed(db)` or `reset_database(db)` from `src.db.seed` directly.

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MONGO_URI` | `mongodb://localhost:27017` | Server address (`mongodb://mongo:27017` inside Docker Compose) |
| `MONGO_DB_NAME` | `hoteltrivago_dev` | Database name |
| `MONGO_TIMEOUT_MS` | `5000` | Fail fast when MongoDB is down (TC-021) |
| `BCRYPT_ROUNDS` | `12` | bcrypt cost; use `4` in tests so they stay fast |
| `SEED_ADMIN_PASSWORD` | — | Replaces `AdminPass123` in deployed demos |

---

## 6. Using it from the backend

```python
from datetime import datetime, timezone

from src.db import get_db, hash_password, hash_token, normalize_email, verify_password

db = get_db()

# Login (TC-005, TC-006): look up by the normalized email, compare with bcrypt.
user = db.users.find_one({"email": normalize_email(email), "status": "active"})
ok = user is not None and verify_password(password, user["password_hash"])

# Reset link (TC-007, TC-008): look up by the hash of the token in the URL.
now = datetime.now(timezone.utc)
reset = db.password_reset_tokens.find_one(
    {"token_hash": hash_token(raw_token), "status": "issued", "expires_at": {"$gt": now}}
)
```

- `email`, `password`, `raw_token` must be checked to be strings before they reach a query (TC-022 a).
- `hash_password()` raises `ValueError` for passwords over 72 bytes, the bcrypt limit.

---

## 7. Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/db --cov=src/db
```

Tests marked `mongo` need a real MongoDB (validators and TTL indexes do not exist in mongomock) and are skipped when none is reachable at `MONGO_TEST_URI` (default `mongodb://localhost:27017`). To run them locally:

```bash
docker run -d --name mongo-test -p 27017:27017 mongo:7
```

The seed tests also check the seed against the QA data files (`tests/data/price-filter.csv`, the TC-015 filters and the TC-016 sort orders).

---

## 8. Pending agreements

| With | Topic |
| --- | --- |
| DevOps | `mongo` service in `docker-compose.yml` (TC-021 uses that name), a named volume, `MONGO_URI` and `MONGO_DB_NAME` in `.env.example`, `make seed` / `make db-reset`, and a MongoDB service in CI for the `mongo` tests |
| Backend | PyMongo (synchronous, fits Flask) instead of Motor; sessions as JWT `jti` + the `sessions` collection; where uploaded room photos are stored (only the URL goes in MongoDB) |
| QA | Add U-04 and U-05 to `tests/data/test-data.md`; whether search filters by room capacity (TC-009 expects R-005, max 1 guest, for 2 guests in 1 room) |
| Frontend | Labels for the codes (`wifi`, `balcony`, `minibar`, `single`, `double`, `suite`) and the 7 seed photos under `/images/rooms/` |
