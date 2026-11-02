# Test Data — HotelTrivago

**Milestone**: M3 — Black Box Testing (reused in M4–M7)
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-11-01

Synthetic data used by the test cases in [`docs/milestones/M3/test-cases.md`](../../docs/milestones/M3/test-cases.md). It must be aligned with the seed datasets maintained by the DB Lead.

---

## 1. Rules

- **No real personal data.** All emails use the reserved `example.com` domain.
- **Relative dates.** `TODAY` is the execution date; `TODAY+7` means 7 days later. Automated tests compute them at runtime.
- **Known starting state.** Every test case starts from this seed; the test database is reset between suites (and between cases that modify data, e.g. TC-007 changes `U-02`'s password).
- **Prices** are static, per night, in MXN (single hotel, no providers).

---

## 2. Test Users

```json
{
  "U-01": { "email": "client1@example.com", "password": "Client1Pass", "role": "user" },
  "U-02": { "email": "client2@example.com", "password": "Client2Pass", "role": "user" },
  "U-03": { "email": "admin@example.com", "password": "AdminPass123", "role": "admin" },
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
| U-01 | Main client: login/logout, session persistence                          |
| U-02 | Second client: password reset                                           |
| U-03 | Admin: employee portal, room CRUD, RBAC                                 |

---

## 3. Rooms

| ID    | Name            | Room type | Amenities               | Price/night |
| ----- | --------------- | --------- | ----------------------- | ----------- |
| R-001 | Standard Double | Double    | Wi-Fi                   | 1000        |
| R-002 | Deluxe Double   | Double    | Wi-Fi, Balcony          | 1500        |
| R-003 | Junior Suite    | Suite     | Wi-Fi, Minibar          | 2000        |
| R-004 | Master Suite    | Suite     | Wi-Fi, Balcony, Minibar | 2500        |
| R-005 | Single          | Single    | —                       | 450         |

- `R-002` has **3 photos** (TC-017).

**Expected orders for the TC-009 search (TC-016)**:

| Sort               | Order                                 |
| ------------------ | ------------------------------------- |
| Price ascending    | R-005, R-001, R-002, R-003, R-004     |
| Price descending   | R-004, R-003, R-002, R-001, R-005     |

---

## 4. Data Files

| File                                                   | Used by                 | Description                                        |
| ------------------------------------------------------ | ----------------------- | -------------------------------------------------- |
| [`registration-valid.csv`](./registration-valid.csv)   | TC-001, TC-003          | Registrations that must succeed                    |
| [`registration-invalid.csv`](./registration-invalid.csv) | TC-002, TC-003, TC-004 | Registrations that must fail and the expected error |
| [`search-criteria.csv`](./search-criteria.csv)         | TC-010, TC-011, TC-012, TC-013 | Search inputs (relative dates) and expected outcome |
| [`price-filter.csv`](./price-filter.csv)               | TC-014                  | Price ranges and expected room IDs                 |

These files will feed the parameterized (data-driven) tests in later milestones.
