# Test Data — HotelTrivago

**Milestone**: M3 — Black Box Testing (reused in M4–M7)
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-10-26

Synthetic data used by the test cases in [`docs/milestones/M3/test-cases.md`](../../docs/milestones/M3/test-cases.md). It must be aligned with the seed datasets maintained by the DB Lead.

---

## 1. Rules

- **No real personal data.** All emails use the reserved `example.com` domain.
- **Relative dates.** `TODAY` is the execution date; `TODAY+7` means 7 days later. Automated tests compute them at runtime.
- **Known starting state.** Every test case starts from this seed; the test database is reset between suites (and between cases that modify data, e.g. TC-007 changes `U-02`'s password).
- **Prices** are per night, in MXN, and equal the lowest provider price for the hotel.

---

## 2. Test Users

```json
{
  "U-01": { "email": "client1@example.com", "password": "Client1Pass", "role": "user" },
  "U-02": { "email": "client2@example.com", "password": "Client2Pass", "role": "user" },
  "U-03": { "email": "admin@example.com", "password": "AdminPass123", "role": "admin" },
  "U-04": { "email": "reviewer@example.com", "password": "Reviewer1Pass", "role": "user" },
  "invalid_users": [
    { "email": "userexample.com", "password": "ValidPass123", "reason": "missing @" },
    { "email": "user@", "password": "ValidPass123", "reason": "missing domain" },
    { "email": "", "password": "ValidPass123", "reason": "email required" },
    { "email": "short-pwd@example.com", "password": "Abcde12", "reason": "password too short" }
  ]
}
```

| User | Purpose                                                                 |
| ---- | ----------------------------------------------------------------------- |
| U-01 | Main client: login, favorites, history, review `RV-02` on H-002         |
| U-02 | Second client: author of review `RV-01`, password reset, isolation checks |
| U-03 | Admin: employee portal, hotel CRUD, moderation                          |
| U-04 | Client with **no reviews**, used for review boundary tests (TC-026, TC-027) |

---

## 3. Hotels

| ID    | Name                    | City            | Stars | Guest rating | Type      | Amenities            | Price/night | Distance to center (km) | Popularity | Coordinates          |
| ----- | ----------------------- | --------------- | ----- | ------------ | --------- | -------------------- | ----------- | ----------------------- | ---------- | -------------------- |
| H-001 | Hotel Centro Histórico  | Guadalajara     | 3     | 8.1          | Hotel     | Wi-Fi                | 1000        | 0.5                     | 120        | 20.6767, −103.3475   |
| H-002 | Casa Chapultepec        | Guadalajara     | 4     | 8.9          | Hotel     | Wi-Fi, Pool          | 1500        | 2.0                     | 300        | 20.6736, −103.3700   |
| H-003 | Suites Minerva          | Guadalajara     | 4     | 7.5          | Apartment | Wi-Fi, Parking       | 2000        | 3.5                     | 80         | 20.6743, −103.3874   |
| H-004 | Grand Providencia       | Guadalajara     | 5     | 9.2          | Hotel     | Wi-Fi, Pool, Parking | 2500        | 4.0                     | 450        | 20.6953, −103.3811   |
| H-005 | Hostal Expiatorio       | Guadalajara     | 2     | 6.8          | Hostel    | —                    | 450         | 1.0                     | 60         | **none** (TC-023)    |
| H-006 | Hotel Malecón           | Puerto Vallarta | 4     | 8.6          | Hotel     | Wi-Fi, Pool          | 2200        | 0.8                     | 260        | 20.6100, −105.2330   |

- `Tepic` is a **known destination with no hotels** (empty state, TC-013).
- `H-002` has **3 photos** and **2 reviews** (`RV-01`, `RV-02`).

**Expected orders for the Guadalajara search (TC-016)**:

| Sort               | Order                                 |
| ------------------ | ------------------------------------- |
| Price ascending    | H-005, H-001, H-002, H-003, H-004     |
| Price descending   | H-004, H-003, H-002, H-001, H-005     |
| Guest rating       | H-004, H-002, H-001, H-003, H-005     |
| Distance           | H-001, H-005, H-002, H-003, H-004     |
| Popularity         | H-004, H-002, H-001, H-003, H-005     |

---

## 4. Reviews

| ID    | Hotel | Author | Rating | Text                                   | State     |
| ----- | ----- | ------ | ------ | -------------------------------------- | --------- |
| RV-01 | H-002 | U-02   | 4      | "Great pool and very helpful staff."   | Published |
| RV-02 | H-002 | U-01   | 5      | "Perfect location to explore the city." | Published |

---

## 5. Booking Providers (stubs)

| ID   | Name        | Default stub mode | Default price for H-002 |
| ---- | ----------- | ----------------- | ----------------------- |
| P-01 | Booking     | OK                | 1500                    |
| P-02 | Expedia     | OK                | 1600                    |
| P-03 | Hotel site  | OK                | 1550                    |

**Stub modes** (configurable per test):

| Mode              | Behavior                                         |
| ----------------- | ------------------------------------------------ |
| `OK`              | Returns the configured price and a deal URL      |
| `NO_AVAILABILITY` | Returns `200` with no availability for the dates |
| `TIMEOUT`         | Does not respond before the client timeout       |
| `ERROR_500`       | Returns HTTP 500                                 |

Each stub counts the calls it receives (used by TC-018 and TC-020 to verify caching).

---

## 6. Data Files

| File                                                   | Used by                 | Description                                        |
| ------------------------------------------------------ | ----------------------- | -------------------------------------------------- |
| [`registration-valid.csv`](./registration-valid.csv)   | TC-001, TC-003          | Registrations that must succeed                    |
| [`registration-invalid.csv`](./registration-invalid.csv) | TC-002, TC-003, TC-004 | Registrations that must fail and the expected error |
| [`search-criteria.csv`](./search-criteria.csv)         | TC-010, TC-011, TC-012, TC-013 | Search inputs (relative dates) and expected outcome |
| [`price-filter.csv`](./price-filter.csv)               | TC-014                  | Price ranges and expected hotel IDs                |
| [`review-boundaries.csv`](./review-boundaries.csv)     | TC-026, TC-027          | Rating and text-length boundaries                  |

These files will feed the parameterized (data-driven) tests in later milestones.
