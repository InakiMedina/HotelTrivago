# Traceability Matrix — HotelTrivago

**Milestone**: M3 — Black Box Testing
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-10-26

Maps every requirement to the test cases that verify it. Coverage = share of the requirement's acceptance points (listed in *What is verified*) that have at least one designed test case. Execution status is updated from M4 onward.

---

## 1. Functional Requirements

| Req ID | Requirement                                    | Priority | Test Cases                              | What is verified                                                        | Coverage |
| ------ | ---------------------------------------------- | -------- | --------------------------------------- | ----------------------------------------------------------------------- | -------- |
| FR-1   | Register with email and password               | High     | TC-001, TC-002, TC-003, TC-004, TC-036  | Valid registration, email format, password length, duplicates, hashing  | 100%     |
| FR-2   | Log in and log out                             | High     | TC-005, TC-006, TC-036                  | Valid login/logout, invalid credentials, token reuse, injection         | 100%     |
| FR-3   | Reset password via email link                  | Medium   | TC-007, TC-008                          | Valid reset, used/expired/superseded links, unknown email               | 100%     |
| FR-4   | Search by destination, dates, guests, rooms    | High     | TC-009, TC-010, TC-011, TC-012, TC-013  | Valid search, date and nights limits, guests, rooms, destination partitions | 100% |
| FR-5   | Filter by price, stars, rating, type, amenities | High    | TC-014, TC-015, TC-023                  | Price bounds, each filter type, combined filters, empty state, map sync | 100%     |
| FR-6   | Sort by price, rating, distance, popularity    | Medium   | TC-016                                  | Each sort option, sort with filters, invalid option                     | 100%     |
| FR-7   | Hotel detail page                              | Medium   | TC-017                                  | Photos, description, amenities, location, reviews, invalid IDs          | 100%     |
| FR-8   | Compare prices across providers                | High     | TC-018, TC-019, TC-020, TC-021          | Fresh cache, live refresh, no availability, partial and total failures  | 100%     |
| FR-9   | Redirect to provider                           | High     | TC-022                                  | Redirect URL and parameters, unavailable provider                       | 100%     |
| FR-10  | Results on interactive map                     | Low      | TC-023                                  | Markers, popup, filter sync, missing coordinates                        | 100%     |
| FR-11  | Favorites list                                 | Medium   | TC-024                                  | Add, remove, duplicates, per-user isolation, anonymous user             | 100%     |
| FR-12  | Recent search history and re-run               | Low      | TC-025                                  | History size limit, order, re-run                                       | 100%     |
| FR-13  | Submit, edit and delete reviews                | Medium   | TC-026, TC-027, TC-028, TC-029, TC-030, TC-033, TC-036 | Rating and text limits, lifecycle, permissions, persistence, XSS | 100% |
| FR-14  | Admin hotel CRUD                               | High     | TC-031, TC-032                          | Create/read/update/delete, validation, admin-only access                | 100%     |
| FR-15  | Admin providers/price feeds and review moderation | Medium | TC-020, TC-032, TC-033                 | Price feed refresh, admin-only access, review removal                   | 67% ⚠️   |

> ⚠️ **FR-15 gap**: the admin screens to **create, edit and disable booking providers** have no dedicated test case yet. They will be added once the Backend Lead defines the provider model in `contracts/openapi.yaml` (tracked as an open item).

---

## 2. Non-Functional Requirements

| Req ID     | Requirement                                            | Test Cases / Plan                    | Milestone | Coverage |
| ---------- | ------------------------------------------------------ | ------------------------------------ | --------- | -------- |
| NFR-PERF-1 | Page loads and search < 2 s                            | JMeter load test on search           | M7        | Planned  |
| NFR-PERF-2 | ≥ 100 concurrent users                                 | JMeter load test (100 threads)       | M7        | Planned  |
| NFR-PERF-3 | DB queries < 500 ms (indexes)                          | Query timing + index checks          | M7        | Planned  |
| NFR-PERF-4 | Provider prices cached 15 min                          | TC-018, TC-020                       | M3        | 100%     |
| NFR-SEC-1  | Passwords hashed with bcrypt                           | TC-001 (step 5)                      | M3        | 100%     |
| NFR-SEC-2  | Input validated and sanitized (injection, XSS)         | TC-036, TC-002, TC-010–TC-014        | M3        | 100%     |
| NFR-SEC-3  | Admin routes protected by RBAC                         | TC-032, TC-033                       | M3        | 100%     |
| NFR-SEC-4  | Secure tokens and HTTPS                                | TC-005 (token invalidation); HTTPS check on deployed env | M3 / M7 | 50% |
| NFR-SEC-5  | Rate limiting on search endpoints                      | To be designed with the API contract | M4        | 0% ⚠️    |
| NFR-USA-1  | Responsive design (mobile, tablet, desktop)            | E2E viewport runs of TC-009, TC-017  | M6        | Planned  |
| NFR-USA-2  | Search bar always visible on home and results          | TC-009 (steps 1, 3)                  | M3        | 100%     |
| NFR-USA-3  | Clear, actionable error messages                       | TC-002, TC-010, TC-013, TC-034, TC-035 | M3      | 100%     |
| NFR-USA-4  | Loading indicators and empty states                    | TC-009, TC-013, TC-015, TC-034       | M3        | 100%     |
| NFR-REL-1  | Results still shown if a provider fails                | TC-019, TC-021                       | M3        | 100%     |
| NFR-REL-2  | 99% availability during demo                           | Monitoring during demo               | M7        | Out of scope |
| NFR-TST-1  | ≥ 80% code coverage                                    | Coverage reports in CI               | M4        | Planned  |
| NFR-TST-2  | E2E flow search → filter → view hotel → redirect      | TC-009 → TC-015 → TC-017 → TC-022 (automated as one scenario) | M6 | Planned |
| NFR-TST-3  | CI runs all tests and blocks failing merges            | DevOps pipeline                      | M2 / M4   | Planned  |

---

## 3. Coverage Summary

| Group                     | Requirements | Fully covered | Partially covered | Not covered yet | Planned for later milestones | Out of scope |
| ------------------------- | ------------ | ------------- | ----------------- | --------------- | ---------------------------- | ------------ |
| Functional (High)         | 7            | 7 (100%)      | 0                 | 0               | 0                            | 0            |
| Functional (Medium / Low) | 8            | 7             | 1 (FR-15)         | 0               | 0                            | 0            |
| Non-functional            | 18           | 8             | 1 (SEC-4)         | 1 (SEC-5)       | 7                            | 1 (REL-2)    |

**Result**: 100% of **High** priority functional requirements are traced to at least one test case (M3 goal met).

---

## 4. Reverse Traceability (Test Case → Requirement)

| Test Case | Requirements          | Test Case | Requirements          |
| --------- | --------------------- | --------- | --------------------- |
| TC-001    | FR-1, NFR-SEC-1       | TC-019    | FR-8, NFR-REL-1       |
| TC-002    | FR-1, NFR-USA-3       | TC-020    | FR-8, FR-15, NFR-PERF-4 |
| TC-003    | FR-1                  | TC-021    | FR-8, NFR-REL-1       |
| TC-004    | FR-1                  | TC-022    | FR-9                  |
| TC-005    | FR-2, NFR-SEC-4       | TC-023    | FR-10, FR-5           |
| TC-006    | FR-2                  | TC-024    | FR-11                 |
| TC-007    | FR-3                  | TC-025    | FR-12                 |
| TC-008    | FR-3                  | TC-026    | FR-13                 |
| TC-009    | FR-4, NFR-USA-2       | TC-027    | FR-13                 |
| TC-010    | FR-4, NFR-USA-3       | TC-028    | FR-13                 |
| TC-011    | FR-4                  | TC-029    | FR-13                 |
| TC-012    | FR-4                  | TC-030    | FR-13                 |
| TC-013    | FR-4, NFR-USA-3/4     | TC-031    | FR-14                 |
| TC-014    | FR-5                  | TC-032    | FR-14, FR-15, NFR-SEC-3 |
| TC-015    | FR-5, NFR-USA-4       | TC-033    | FR-15, FR-13, NFR-SEC-3 |
| TC-016    | FR-6                  | TC-034    | NFR-USA-3/4           |
| TC-017    | FR-7                  | TC-035    | NFR-USA-3             |
| TC-018    | FR-8, NFR-PERF-4      | TC-036    | NFR-SEC-2, FR-1, FR-2, FR-13 |
