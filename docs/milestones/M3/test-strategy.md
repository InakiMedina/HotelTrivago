# Test Strategy — HotelTrivago

**Milestone**: M3 — Black Box Testing
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-11-01
**Status**: Draft — pending team review

---

## 1. Purpose

This document defines how the HotelTrivago team will verify that the application meets the functional and non-functional requirements described in the requirements specification (FR-1 to FR-15 and the NFRs). It sets the scope, test levels, techniques, environments, entry/exit criteria and defect process that all milestones (M3–M7) will follow.

Related documents:

- [Test Plan](./test-plan.md) — features, priorities, techniques, business rules, decision tables and state diagrams
- [Test Cases](./test-cases.md) — detailed black box test cases (TC-001 to TC-023)
- [Traceability Matrix](./traceability-matrix.md) — requirements → test cases
- [Test Data](../../../tests/data/test-data.md) — test users and data sets

---

## 2. Testing Scope

### 2.1 In Scope

| Area                         | Requirements          | Notes                                                       |
| ---------------------------- | --------------------- | ----------------------------------------------------------- |
| User management              | FR-1, FR-2, FR-3      | Registration, login/logout, password reset                  |
| Search, filter and sort      | FR-4, FR-5, FR-6      | Input validation, result correctness, empty states          |
| Room detail                  | FR-7                  | Content, missing/invalid room                               |
| Admin features               | FR-14                 | Room CRUD, RBAC                                             |
| Security (functional checks) | NFR Security          | Input sanitization, RBAC, password hashing, no user leakage |
| Usability (functional)       | NFR Usability         | Error messages, empty states, loading indicators            |
| API endpoints                | All FRs               | Status codes, payload validation (once the contract exists) |

### 2.2 Out of Scope (for M3)

- **Performance and load testing** (2 s page load, 100 concurrent users, 500 ms queries) — planned for **M7** with JMeter.
- **Security penetration testing** — only functional security checks are included.
- **Descoped in the PR review** (single hotel, static prices): providers and price comparison (FR-8, FR-9), map (FR-10), favorites and search history (FR-11, FR-12), reviews and moderation (FR-13, FR-15).
- **Email delivery infrastructure** — reset emails are captured with a test mail catcher, not delivered.
- **Cross-browser matrix beyond Chromium, Firefox and WebKit** and real mobile devices (responsive checks use emulated viewports).
- **99% availability target** — monitored during the demo period, not tested.

---

## 3. Testing Approach

### 3.1 Test Levels

| Level             | Milestone | Owner(s)                 | Tooling                                 | Focus                                               |
| ----------------- | --------- | ------------------------ | --------------------------------------- | --------------------------------------------------- |
| Unit              | M4        | Each feature author      | pytest + pytest-cov, mongomock          | Business rules (validation, filters, sorting)       |
| Integration / API | M4        | Backend Lead + QA Lead   | pytest + Flask test client              | Endpoints, MongoDB                                  |
| TDD feature       | M5        | Feature owner            | pytest                                  | Red-Green-Refactor history                          |
| Data-driven       | M5–M7     | QA Lead                  | pytest parametrize, CSV/JSON in `tests/data` | Boundary and partition data sets               |
| System / E2E      | M6        | QA Lead + Frontend Lead  | Playwright, Gherkin features, Page Object Model | User journeys across both portals          |
| Performance       | M7        | QA Lead + DevOps Lead    | JMeter                                  | Search endpoint load, response times                |
| Acceptance        | M7        | Project Manager + team   | Demo checklist                          | Requirements sign-off                               |

### 3.2 Test Types

- **Functional testing** of every FR using the black box techniques below.
- **Boundary testing** for every numeric/date/length input.
- **State transition testing** for entities with a lifecycle (password reset tokens, user session).
- **Negative and error handling testing** (invalid input, network failures, server errors).
- **Authorization testing** (anonymous vs registered user vs admin).
- **Regression testing** — automated suites run in CI on every push (see §7).

### 3.3 Black Box Techniques

| Technique                       | Where it is applied                                                                              |
| ------------------------------- | ------------------------------------------------------------------------------------------------ |
| Equivalence Partitioning (EP)   | Email format, credentials, search fields, filters, sort options, room data                       |
| Boundary Value Analysis (BVA)   | Password length, dates and nights, guests, rooms, price range                                    |
| Decision Tables (DT)            | Admin route access (DT-1)                                                                        |
| State Transition (ST)           | Password reset token (ST-1), user session (ST-2)                                                 |
| Error guessing                  | Injection payloads, network/server errors, duplicate actions                                    |

Details for each technique are in the [Test Plan](./test-plan.md#4-test-design-techniques).

### 3.4 Requirements Gaps → Assumed Business Rules

The requirements do not define limits such as password length or maximum guests. To be able to apply BVA, the test plan defines assumed business rules (BR-01 to BR-06). These must be confirmed by the team; if a value changes, only the affected test data and expected results need updating.

---

## 4. Entry and Exit Criteria

### 4.1 Entry Criteria (to start executing tests of a feature)

- Requirements and acceptance criteria for the feature are agreed (assumed BRs confirmed or replaced).
- Feature code is merged into `beta` and the build passes CI (lint + unit tests).
- The API contract (`contracts/openapi.yaml`) covers the endpoints involved.
- Test environment is up (`docker compose up`) with the seed data loaded.
- Test data from `tests/data/` is available and current.

### 4.2 Exit Criteria (to consider a milestone/release done)

- 100% of **High** priority test cases executed.
- **≥ 90%** of executed test cases passing.
- **0 open Critical/High** severity defects; Medium/Low defects documented with an owner.
- Code coverage **≥ 80%** (course requirement and NFR Testing).
- Traceability matrix updated: every FR has at least one executed test case.
- Test execution results recorded (status, executor, date) in the test cases or test report.

### 4.3 Suspension and Resumption Criteria

- **Suspend** a test cycle if the environment is down, seed data is corrupted, or a blocker defect prevents > 30% of the planned cases from running.
- **Resume** once the blocker is fixed and a smoke test (login + basic search) passes.

---

## 5. Test Environment

| Environment | Description                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------- |
| Local / Dev | `docker compose up` — backend (`:8000`), frontend Vite MPA (`:5173/client/`, `:5173/employee/`), MongoDB (`:27017`) |
| CI          | GitHub Actions running lint, unit/integration tests and E2E against containers                    |
| Demo / AWS  | Deployed environment used for M7 performance tests and the final demo                             |

**Test data rules**:

- Synthetic data only — **no real personal data (PII)**.
- Dates are expressed **relative to the execution date** (`TODAY`, `TODAY+N`) so cases do not expire.
- Each automated run starts from a known seed (dedicated test database, reset between suites).
- Reset emails are captured by a local mail catcher (e.g. Mailpit) to read the reset link.

---

## 6. Roles and Responsibilities

| Member                         | Role          | Testing responsibilities                                                    |
| ------------------------------ | ------------- | --------------------------------------------------------------------------- |
| Gilberto Anaya Mercado         | QA Lead       | Strategy, test plan, test cases, E2E suite, API checks, bug triage, reports |
| Inaki Medina Munguia           | Project Manager | Confirms acceptance criteria and assumed business rules, acceptance tests  |
| Isaac Ernesto Vasquez Sandoval | Backend Lead  | Unit/integration tests for API, API contract                                |
| Carlos Emilio Olmedo Navarro   | Frontend Lead | Testable UI (stable selectors), support for E2E page objects                |
| Angel Isaac Barbarin Cuevas    | DB Lead       | Seed and test datasets, index verification for query NFRs                   |
| Fabian Patricio Gaxiola Valades | DevOps Lead  | CI pipeline running all suites, test environments, merge blocking           |

---

## 7. Defect Management

- Defects are tracked as **GitHub Issues** with the `bug` label and a severity label.
- Each defect references the test case that found it (e.g. "Found by TC-014").

| Severity | Definition                                                         | Example                                     |
| -------- | ------------------------------------------------------------------ | ------------------------------------------- |
| Critical | Blocks a core flow or exposes data/security; no workaround         | Non-admin can delete rooms                  |
| High     | Core feature gives wrong results; workaround is hard               | Price filter excludes rooms at the boundary  |
| Medium   | Feature partially wrong; reasonable workaround                     | Sort by price ignores ties order            |
| Low      | Cosmetic or wording issue                                          | Typo in error message                       |

**Workflow**: Open → In progress → Fixed (PR linked) → Verified by QA → Closed. A fix must include a regression test (test-driven bug fix, as required in M4).

---

## 8. Risks and Mitigations

| Risk                                                                 | Impact | Mitigation                                                                 |
| -------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------- |
| Requirements lack limits and acceptance criteria                     | High   | Assumed BRs documented and reviewed with PM; matrix updated on changes     |
| Front end and back end not started yet                               | High   | Design tests now from requirements; automate as features land              |
| API contract (`openapi.yaml`) still empty                             | Medium | Agree contract with Backend Lead before writing API tests                  |
| Date-dependent tests become flaky                                    | Medium | Relative dates and frozen clock in unit tests                              |
| Schedule pressure near milestones                                     | Medium | Prioritize High cases; automate smoke suite first                          |

---

## 9. Team Decisions and Open Questions

Decisions from the PR review:

- Single hotel with static room prices. So no providers and no price cache.
- No favorites, search history or reviews in the MVP.
- Coverage threshold: 80%, also for merges into beta.
- Injection tests use NoSQL operator injection (e.g. {"$ne": null}) instead of SQL injection.
- Backend is Flask; API tests use the Flask test client.

Open questions:

1. Can clients book a room, or only see rooms and prices?
2. Are the limits in the [business rules](./test-plan.md#3-assumed-business-rules) (BR-01 to BR-06) OK?
