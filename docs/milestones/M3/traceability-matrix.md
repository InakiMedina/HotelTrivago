# Traceability Matrix — HotelTrivago

**Milestone**: M3 — Black Box Testing
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-11-01

Maps every requirement to the test cases that verify it. Coverage = share of the requirement's acceptance points (listed in *What is verified*) that have at least one designed test case. Execution status is updated from M4 onward.

---

## 1. Functional Requirements

| Req ID | Requirement                                    | Priority | Test Cases                              | What is verified                                                        | Coverage |
| ------ | ---------------------------------------------- | -------- | --------------------------------------- | ----------------------------------------------------------------------- | -------- |
| FR-1   | Register with email and password               | High     | TC-001, TC-002, TC-003, TC-004          | Valid registration, email format, password length, duplicates, hashing  | 100%     |
| FR-2   | Log in and log out                             | High     | TC-005, TC-006, TC-022, TC-023          | Valid login/logout, invalid credentials, token reuse/expiry, injection, persistence | 100% |
| FR-3   | Reset password via email link                  | Medium   | TC-007, TC-008, TC-023                  | Valid reset, used/expired/superseded links, unknown email, persistence  | 100%     |
| FR-4   | Search rooms by dates, guests, rooms           | High     | TC-009, TC-010, TC-011, TC-012, TC-013  | Valid search, date and nights limits, guests, rooms, missing/invalid fields | 100% |
| FR-5   | Filter by price, room type, amenities          | High     | TC-014, TC-015                          | Price bounds, each filter type, combined filters, empty state           | 100%     |
| FR-6   | Sort by price                                  | Medium   | TC-016                                  | Each sort option, sort with filters, invalid option                     | 100%     |
| FR-7   | Room detail page                               | Medium   | TC-017, TC-022                          | Photos, description, amenities, price, invalid IDs, injection           | 100%     |
| FR-14  | Admin room CRUD                                | High     | TC-018, TC-019, TC-022                  | Create/read/update/delete, validation, admin-only access, XSS           | 100%     |

> FR-8 – FR-13 and FR-15 were descoped in the PR review (single hotel, static prices, no favorites, history or reviews), so they have no test cases.

---

## 2. Non-Functional Requirements

| Req ID     | Requirement                                            | Test Cases / Plan                    | Milestone | Coverage |
| ---------- | ------------------------------------------------------ | ------------------------------------ | --------- | -------- |
| NFR-PERF-1 | Page loads and search < 2 s                            | JMeter load test on search           | M7        | Planned  |
| NFR-PERF-2 | ≥ 100 concurrent users                                 | JMeter load test (100 threads)       | M7        | Planned  |
| NFR-PERF-3 | DB queries < 500 ms (indexes)                          | Query timing + index checks          | M7        | Planned  |
| NFR-PERF-4 | Provider prices cached 15 min                          | Descoped (no providers)              | —         | N/A      |
| NFR-SEC-1  | Passwords hashed with bcrypt                           | TC-001 (step 5)                      | M3        | 100%     |
| NFR-SEC-2  | Input validated and sanitized (NoSQL injection, XSS)   | TC-022, TC-013                       | M3        | 100%     |
| NFR-SEC-3  | Admin routes protected by RBAC                         | TC-019                               | M3        | 100%     |
| NFR-SEC-4  | Secure tokens and HTTPS                                | TC-005 (token invalidation); HTTPS check on deployed env | M3 / M7 | 50% |
| NFR-SEC-5  | Rate limiting on search endpoints                      | To be designed with the API contract | M4        | 0% ⚠️    |
| NFR-USA-1  | Search bar always visible on home and results          | TC-009 (steps 1, 3)                  | M3        | 100%     |
| NFR-USA-2  | Clear, actionable error messages                       | TC-002, TC-010, TC-013, TC-020, TC-021 | M3      | 100%     |
| NFR-USA-3  | Loading indicators and empty states                    | TC-009, TC-015, TC-020               | M3        | 100%     |
| NFR-REL-1  | Results still shown if a provider fails                | Descoped (no providers)              | —         | N/A      |
| NFR-REL-2  | 99% availability during demo                           | Monitoring during demo               | M7        | Out of scope |
| NFR-TST-1  | ≥ 80% code coverage                                    | Coverage reports in CI               | M4        | Planned  |
| NFR-TST-2  | E2E flow search → filter → view room                   | TC-009 → TC-015 → TC-017 (automated as one scenario) | M6 | Planned |
| NFR-TST-3  | CI runs all tests and blocks failing merges            | DevOps pipeline                      | M2 / M4   | Planned  |

---

## 3. Coverage Summary

| Group                     | Requirements | Fully covered | Partially covered | Not covered yet | Planned for later milestones | Out of scope |
| ------------------------- | ------------ | ------------- | ----------------- | --------------- | ---------------------------- | ------------ |
| Functional (High)         | 5            | 5 (100%)      | 0                 | 0               | 0                            | 0            |
| Functional (Medium / Low) | 3            | 3             | 0                 | 0               | 0                            | 0            |
| Non-functional            | 18           | 6             | 1 (SEC-4)         | 1 (SEC-5)       | 7                            | 3 (REL-2, PERF-4, REL-1) |

**Result**: 100% of **High** priority functional requirements are traced to at least one test case (M3 goal met).

---

## 4. Reverse Traceability (Test Case → Requirement)

| Test Case | Requirements          | Test Case | Requirements          |
| --------- | --------------------- | --------- | --------------------- |
| TC-001    | FR-1, NFR-SEC-1       | TC-013    | FR-4, NFR-USA-2, NFR-SEC-2 |
| TC-002    | FR-1, NFR-USA-3       | TC-014    | FR-5                  |
| TC-003    | FR-1                  | TC-015    | FR-5, NFR-USA-4       |
| TC-004    | FR-1                  | TC-016    | FR-6                  |
| TC-005    | FR-2, NFR-SEC-4       | TC-017    | FR-7                  |
| TC-006    | FR-2                  | TC-018    | FR-14                 |
| TC-007    | FR-3                  | TC-019    | FR-14, NFR-SEC-3      |
| TC-008    | FR-3                  | TC-020    | NFR-USA-2/3           |
| TC-009    | FR-4, NFR-USA-2/4     | TC-021    | NFR-USA-2             |
| TC-010    | FR-4, NFR-USA-3       | TC-022    | NFR-SEC-2, FR-2, FR-7, FR-14 |
| TC-011    | FR-4                  | TC-023    | FR-2, FR-3            |
| TC-012    | FR-4                  |           |                       |
