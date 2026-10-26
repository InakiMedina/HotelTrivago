# Test Cases — HotelTrivago

**Milestone**: M3 — Black Box Testing
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-10-26
**Total test cases**: 36

---

## Conventions

- **Test data** (users `U-xx`, hotels `H-xxx`, providers `P-xx`) is defined in [`tests/data/test-data.md`](../../../tests/data/test-data.md).
- **Dates** are relative to the execution date: `TODAY`, `TODAY+7`, etc.
- **Business rules** `BR-xx`, decision tables `DT-x` and state diagrams `ST-x` are defined in the [Test Plan](./test-plan.md).
- **Execution fields** (Actual Result, Status, Tested By, Date) are filled when the case is executed (M4–M6). Status values: `Not Executed` / `Pass` / `Fail` / `Blocked`.
- Where the UI is not ready, a step can be executed against the API; the expected result applies to both.
- Every test case starts from the **seed state** (database reset), so cases can run in any order.

## Index

| ID     | Title                                                  | Requirement | Technique | Priority |
| ------ | ------------------------------------------------------ | ----------- | --------- | -------- |
| TC-001 | Register with valid data                               | FR-1        | EP        | High     |
| TC-002 | Register with invalid email formats                    | FR-1        | EP        | High     |
| TC-003 | Password length boundaries at registration             | FR-1        | BVA       | High     |
| TC-004 | Register with an already registered email              | FR-1        | EP        | High     |
| TC-005 | Login and logout with valid credentials                | FR-2        | ST        | High     |
| TC-006 | Login with invalid credentials                         | FR-2        | EP        | High     |
| TC-007 | Password reset with a valid link                       | FR-3        | ST        | Medium   |
| TC-008 | Password reset link reused, expired or superseded      | FR-3        | ST        | Medium   |
| TC-009 | Search with valid criteria                             | FR-4        | EP        | High     |
| TC-010 | Check-in date and stay length boundaries               | FR-4        | BVA       | High     |
| TC-011 | Number of guests boundaries                            | FR-4        | BVA       | High     |
| TC-012 | Number of rooms boundaries                             | FR-4        | BVA       | Medium   |
| TC-013 | Search with empty, unknown or hotel-less destination   | FR-4        | EP        | High     |
| TC-014 | Price range filter boundaries                          | FR-5        | BVA       | High     |
| TC-015 | Combined filters                                       | FR-5        | EP        | High     |
| TC-016 | Sort results by each option                            | FR-6        | EP        | Medium   |
| TC-017 | Hotel detail page for existing and non-existing hotel  | FR-7        | EP        | Medium   |
| TC-018 | Provider prices from fresh cache and no availability   | FR-8        | DT        | High     |
| TC-019 | One provider fails, others still shown                 | FR-8        | DT        | High     |
| TC-020 | Stale cache triggers a live price refresh              | FR-8, FR-15 | DT        | Medium   |
| TC-021 | All providers fail                                     | FR-8        | DT        | High     |
| TC-022 | Redirect to the selected provider                      | FR-9        | EP        | High     |
| TC-023 | Map shows the same hotels as the result list           | FR-10       | EP        | Low      |
| TC-024 | Add and remove favorites                               | FR-11       | EP        | Medium   |
| TC-025 | Search history limit and re-run                        | FR-12       | BVA       | Low      |
| TC-026 | Review rating boundaries                               | FR-13       | BVA       | Medium   |
| TC-027 | Review text length boundaries                          | FR-13       | BVA       | Medium   |
| TC-028 | Review lifecycle: submit, edit, delete                 | FR-13       | ST        | Medium   |
| TC-029 | Review permissions for anonymous and non-author users  | FR-13       | DT        | High     |
| TC-030 | Review persists after logout and server restart        | FR-13       | ST        | Medium   |
| TC-031 | Admin creates, updates and deletes a hotel             | FR-14       | EP        | High     |
| TC-032 | Admin route access control                             | FR-14, FR-15 | DT       | High     |
| TC-033 | Admin moderates (removes) a review                     | FR-15       | ST        | Medium   |
| TC-034 | Network error during search                            | NFR-USA     | EP        | Medium   |
| TC-035 | Server error during search                             | NFR-USA     | EP        | Medium   |
| TC-036 | Injection and XSS payloads are rejected or sanitized   | NFR-SEC     | EP        | High     |

---

## 1. User Authentication

### TC-001: Register with valid data

**Requirement**: FR-1 — User registration
**Technique**: Equivalence Partitioning (valid partition)
**Priority**: High
**Preconditions**:

- Application is running; `newuser@example.com` is not registered.

**Test Data**:

| Field            | Value                 | Notes                       |
| ---------------- | --------------------- | --------------------------- |
| Email            | `newuser@example.com` | Valid format, not registered |
| Password         | `ValidPass123`        | 12 chars, letters + digits (BR-01) |
| Confirm password | `ValidPass123`        | Matches                     |

**Test Steps**:

| Step | Action                                         | Expected Result                         |
| ---- | ---------------------------------------------- | --------------------------------------- |
| 1    | Open `/client/` and click **Sign up**          | Registration form is displayed          |
| 2    | Enter email, password and confirm password     | Fields accept input; password is masked |
| 3    | Click **Create account**                       | Request is sent; loading indicator shown |
| 4    | Inspect the response / redirect                | Success message; user is logged in or redirected to login |
| 5    | Query the `users` collection for the email     | One document exists; password is stored as a **bcrypt hash** (starts with `$2`), never in plain text |

**Expected Result**: Account is created (API `201 Created`), the user can log in with the new credentials, and the password is hashed.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-002: Register with invalid email formats

**Requirement**: FR-1 — User registration
**Technique**: Equivalence Partitioning (invalid partitions)
**Priority**: High
**Preconditions**: Registration form is open.

**Test Data** (password always `ValidPass123`):

| # | Email                 | Invalid partition   |
| - | --------------------- | ------------------- |
| a | `userexample.com`     | Missing `@`         |
| b | `user@`               | Missing domain      |
| c | `user name@example.com` | Contains spaces   |
| d | *(empty)*             | Required field empty |

**Test Steps**:

| Step | Action                                    | Expected Result                                       |
| ---- | ----------------------------------------- | ----------------------------------------------------- |
| 1    | Enter email (a) and the valid password    | —                                                     |
| 2    | Click **Create account**                  | Form is not submitted / API returns `400` or `422`    |
| 3    | Read the error message                    | Clear message next to the email field, e.g. "Enter a valid email address" |
| 4    | Repeat steps 1–3 for (b), (c) and (d)     | Same behavior; for (d) the message says the email is required |

**Expected Result**: No account is created for any invalid email; each attempt shows a clear, actionable error.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-003: Password length boundaries at registration

**Requirement**: FR-1 — User registration (BR-01: 8–64 characters)
**Technique**: Boundary Value Analysis
**Priority**: High
**Preconditions**: Registration form is open; each row uses a new unregistered email (`bva-pwd-<n>@example.com`).

**Test Data**:

| # | Password length | Example value                    | Expected        |
| - | --------------- | -------------------------------- | --------------- |
| a | 7               | `Abcde12`                        | ❌ Rejected      |
| b | 8               | `Abcdef12`                       | ✅ Accepted      |
| c | 64              | `A` + 62×`a` + `1`               | ✅ Accepted      |
| d | 65              | `A` + 63×`a` + `1`               | ❌ Rejected      |

**Test Steps**:

| Step | Action                                         | Expected Result                                  |
| ---- | ---------------------------------------------- | ------------------------------------------------ |
| 1    | Enter a new email and password (a) in both password fields | —                                    |
| 2    | Submit the form                                | Rejected with message "Password must be 8–64 characters" |
| 3    | Repeat for (b), (c), (d)                       | (b) and (c) create the account; (d) is rejected  |

**Expected Result**: Only lengths 8 and 64 are accepted; 7 and 65 are rejected with a message stating the allowed range.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-004: Register with an already registered email

**Requirement**: FR-1 — User registration
**Technique**: Equivalence Partitioning (invalid partition: duplicate)
**Priority**: High
**Preconditions**: User `U-01` (`client1@example.com`) exists.

**Test Data**: Email `client1@example.com`, also tested as `CLIENT1@Example.com` (case variant); password `ValidPass123`.

**Test Steps**:

| Step | Action                                                  | Expected Result                                        |
| ---- | ------------------------------------------------------- | ------------------------------------------------------ |
| 1    | Register with `client1@example.com`                     | Rejected (API `409 Conflict`); message "This email is already registered" |
| 2    | Register with `CLIENT1@Example.com`                     | Also rejected (emails are compared case-insensitively) |
| 3    | Count documents in `users` with that email (any case)   | Still exactly 1                                        |

**Expected Result**: Duplicate registrations are rejected and no second account is created.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-005: Login and logout with valid credentials

**Requirement**: FR-2 — Login/logout
**Technique**: State Transition (ST-3: LoggedOut → LoggedIn → LoggedOut, invalid token reuse)
**Priority**: High
**Preconditions**: User `U-01` exists; browser has no session.

**Test Data**: `client1@example.com` / `Client1Pass`

**Test Steps**:

| Step | Action                                                  | Expected Result                                         |
| ---- | ------------------------------------------------------- | ------------------------------------------------------- |
| 1    | Open `/client/`, click **Log in**, enter credentials, submit | Logged in; header shows the user's email/name and **Log out** |
| 2    | Open **My favorites**                                   | Page loads (protected route accessible)                 |
| 3    | Copy the auth token / session cookie (DevTools)         | —                                                       |
| 4    | Click **Log out**                                       | Redirected to home; **Log in** is shown again           |
| 5    | Open **My favorites**                                   | Redirected to login                                     |
| 6    | Call `GET /favorites` with the copied old token          | `401 Unauthorized` (token invalidated on logout)        |

**Expected Result**: Valid transitions LoggedOut → LoggedIn → LoggedOut work; the old token cannot be reused after logout.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-006: Login with invalid credentials

**Requirement**: FR-2 — Login/logout
**Technique**: Equivalence Partitioning (invalid partitions)
**Priority**: High
**Preconditions**: User `U-01` exists; no session.

**Test Data**:

| # | Email                    | Password       | Partition        |
| - | ------------------------ | -------------- | ---------------- |
| a | `client1@example.com`    | `WrongPass999` | Wrong password   |
| b | `nobody@example.com`     | `Client1Pass`  | Unknown email    |
| c | *(empty)*                | *(empty)*      | Empty fields     |

**Test Steps**:

| Step | Action                         | Expected Result                                                   |
| ---- | ------------------------------ | ----------------------------------------------------------------- |
| 1    | Submit login with (a)          | `401`; message "Invalid email or password"; user stays logged out |
| 2    | Submit login with (b)          | **Same** message as (a) (no hint whether the email exists)        |
| 3    | Submit login with (c)          | Form validation: "Email and password are required"; no request or `400` |

**Expected Result**: No session is created; messages do not reveal which field was wrong (no user enumeration).

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-007: Password reset with a valid link

**Requirement**: FR-3 — Password reset (BR-08)
**Technique**: State Transition (ST-2: Issued → Used)
**Priority**: Medium
**Preconditions**: User `U-02` exists; mail catcher is running.

**Test Data**: `client2@example.com`; new password `NewPass2024`

**Test Steps**:

| Step | Action                                              | Expected Result                                         |
| ---- | --------------------------------------------------- | ------------------------------------------------------- |
| 1    | On login, click **Forgot password?**, enter the email, submit | Message "If the email exists, we sent a reset link" |
| 2    | Open the email in the mail catcher                   | One email with a reset link containing a token          |
| 3    | Open the link, enter and confirm `NewPass2024`, submit | Message "Password updated"; redirected to login        |
| 4    | Log in with the **old** password `Client2Pass`        | Rejected                                                |
| 5    | Log in with `NewPass2024`                             | Login succeeds                                          |

**Expected Result**: The reset link changes the password once; the old password stops working.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-008: Password reset link reused, expired or superseded

**Requirement**: FR-3 — Password reset (BR-08)
**Technique**: State Transition (ST-2 invalid transitions)
**Priority**: Medium
**Preconditions**: TC-007 executed (a used link exists); ability to set the token creation time in the test DB or a frozen clock.

**Test Data**:

| # | Scenario                                                    | Token state |
| - | ----------------------------------------------------------- | ----------- |
| a | Open the link already used in TC-007                        | Used        |
| b | Request a link, change its creation time to 61 minutes ago, open it | Expired |
| c | Request link #1, then request link #2, open link #1          | Superseded  |
| d | Request a reset for `nobody@example.com`                     | —           |

**Test Steps**:

| Step | Action                         | Expected Result                                                    |
| ---- | ------------------------------ | ------------------------------------------------------------------ |
| 1    | Execute scenario (a)           | Page shows "This link is invalid or has expired"; password unchanged |
| 2    | Execute scenario (b)           | Same message; password unchanged                                   |
| 3    | Execute scenario (c)           | Link #1 rejected; link #2 still works                              |
| 4    | Execute scenario (d)           | Same neutral message as TC-007 step 1; no email is sent            |

**Expected Result**: Only a fresh, unused, latest link can reset the password; responses do not reveal whether an email is registered.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 2. Search, Filter, Sort and Detail

### TC-009: Search with valid criteria

**Requirement**: FR-4 — Search
**Technique**: Equivalence Partitioning (valid partition)
**Priority**: High
**Preconditions**: Seed hotels `H-001`–`H-005` (Guadalajara) loaded; providers in `OK` mode.

**Test Data**: Destination `Guadalajara`; check-in `TODAY+7`; check-out `TODAY+9`; guests 2; rooms 1.

**Test Steps**:

| Step | Action                                    | Expected Result                                        |
| ---- | ----------------------------------------- | ------------------------------------------------------ |
| 1    | Open `/client/`                           | Search bar is visible on the home page                 |
| 2    | Enter the test data and click **Search**  | Loading indicator is shown while searching             |
| 3    | Observe the results page                  | 5 hotels (`H-001`–`H-005`), none from other cities; search bar still visible |
| 4    | Check each result card                    | Name, stars, guest rating, lowest price for **2 nights**, photo |

**Expected Result**: Only Guadalajara hotels are listed with prices for the selected dates.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-010: Check-in date and stay length boundaries

**Requirement**: FR-4 — Search (BR-02, BR-03)
**Technique**: Boundary Value Analysis
**Priority**: High
**Preconditions**: Same as TC-009. Destination `Guadalajara`, guests 2, rooms 1.

**Test Data**:

| # | Check-in  | Check-out  | Nights | Boundary            | Expected   |
| - | --------- | ---------- | ------ | ------------------- | ---------- |
| a | TODAY−1   | TODAY+1    | 2      | Check-in min − 1    | ❌ Rejected |
| b | TODAY     | TODAY+1    | 1      | Check-in min        | ✅ Results  |
| c | TODAY+7   | TODAY+7    | 0      | Nights min − 1      | ❌ Rejected |
| d | TODAY+7   | TODAY+8    | 1      | Nights min          | ✅ Results  |
| e | TODAY+7   | TODAY+37   | 30     | Nights max          | ✅ Results  |
| f | TODAY+7   | TODAY+38   | 31     | Nights max + 1      | ❌ Rejected |

**Test Steps**:

| Step | Action                                   | Expected Result                                               |
| ---- | ---------------------------------------- | ------------------------------------------------------------- |
| 1    | Search with row (a)                      | Error "Check-in date can't be in the past"; no search request or API `422` |
| 2    | Repeat with rows (b)–(f)                 | (b), (d), (e) return results; (c) "Check-out must be after check-in"; (f) "Stays are limited to 30 nights" |

**Expected Result**: Only rows (b), (d), (e) are accepted; rejected rows show a specific message.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-011: Number of guests boundaries

**Requirement**: FR-4 — Search (BR-04: guests 1–10)
**Technique**: Boundary Value Analysis
**Priority**: High
**Preconditions**: Destination `Guadalajara`, `TODAY+7` → `TODAY+9`, rooms 1.

**Test Data**: guests = 0 ❌, 1 ✅, 10 ✅, 11 ❌

**Test Steps**:

| Step | Action                                           | Expected Result                                   |
| ---- | ------------------------------------------------ | ------------------------------------------------- |
| 1    | Try to set guests to 0 with the UI stepper        | The minus button is disabled at 1                 |
| 2    | Call the search API with `guests=0`               | `422` with message about the guest range          |
| 3    | Search with guests 1 and 10                      | Results are returned                              |
| 4    | Try guests 11 (UI and API)                        | UI plus button disabled at 10; API returns `422`  |

**Expected Result**: Values 1 and 10 are accepted; 0 and 11 are rejected both in the UI and the API.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-012: Number of rooms boundaries

**Requirement**: FR-4 — Search (BR-04: rooms 1–5, rooms ≤ guests)
**Technique**: Boundary Value Analysis
**Priority**: Medium
**Preconditions**: Destination `Guadalajara`, `TODAY+7` → `TODAY+9`.

**Test Data**:

| # | Guests | Rooms | Expected   |
| - | ------ | ----- | ---------- |
| a | 2      | 0     | ❌ Rejected |
| b | 2      | 1     | ✅ Accepted |
| c | 10     | 5     | ✅ Accepted |
| d | 10     | 6     | ❌ Rejected |
| e | 3      | 3     | ✅ Accepted (rooms = guests) |
| f | 3      | 4     | ❌ Rejected (rooms > guests) |

**Test Steps**:

| Step | Action                                   | Expected Result                                         |
| ---- | ---------------------------------------- | ------------------------------------------------------- |
| 1    | Search with each row (UI and API)        | Accepted rows return results; rejected rows return `422` and a message such as "Each room needs at least one guest" |

**Expected Result**: Only rows (b), (c), (e) are accepted.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-013: Search with empty, unknown or hotel-less destination

**Requirement**: FR-4 — Search; NFR Usability (error messages, empty states)
**Technique**: Equivalence Partitioning (invalid partitions)
**Priority**: High
**Preconditions**: Dates `TODAY+7` → `TODAY+9`, guests 2, rooms 1. City `Tepic` exists with no hotels.

**Test Data**:

| # | Destination     | Partition                    |
| - | --------------- | ---------------------------- |
| a | *(empty)*       | Empty                        |
| b | `"   "`         | Whitespace only              |
| c | `Xyzqwerty`     | Unknown destination          |
| d | `Tepic`         | Known city with no hotels    |

**Test Steps**:

| Step | Action                         | Expected Result                                                              |
| ---- | ------------------------------ | ---------------------------------------------------------------------------- |
| 1    | Search with (a) and (b)        | Not submitted; message "Enter a destination"                                 |
| 2    | Search with (c)                | Empty state: "We couldn't find that destination. Check the spelling."        |
| 3    | Search with (d)                | Empty state: "No hotels found for these dates. Try changing your filters."   |

**Expected Result**: No crash or blank page; each partition shows a clear, actionable message.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-014: Price range filter boundaries

**Requirement**: FR-5 — Filters (BR-05: inclusive bounds, `0 ≤ min ≤ max`)
**Technique**: Boundary Value Analysis
**Priority**: High
**Preconditions**: TC-009 search executed. Per-night prices: `H-005` 450, `H-001` 1000, `H-002` 1500, `H-003` 2000, `H-004` 2500.

**Test Data**:

| # | Min  | Max  | Expected hotels      | Boundary                     |
| - | ---- | ---- | -------------------- | ---------------------------- |
| a | 1500 | 2000 | H-002, H-003         | Both prices on the bounds (inclusive) |
| b | 1500 | 1999 | H-002                | Max − 1 excludes H-003       |
| c | 1501 | 2000 | H-003                | Min + 1 excludes H-002       |
| d | 1500 | 1500 | H-002                | min = max                    |
| e | 0    | 450  | H-005                | Min lower bound 0            |
| f | −1   | 1000 | — (rejected)         | Min − 1                      |
| g | 2000 | 1500 | — (rejected)         | min > max                    |

**Test Steps**:

| Step | Action                                           | Expected Result                                        |
| ---- | ------------------------------------------------ | ------------------------------------------------------ |
| 1    | Apply the price filter with row (a)              | Exactly the expected hotels; result count updates       |
| 2    | Repeat with rows (b)–(e)                         | Exactly the expected hotels for each row                |
| 3    | Try rows (f) and (g)                             | UI prevents the value or shows "Min price must be between 0 and max price"; API returns `422` |

**Expected Result**: Bounds are inclusive and invalid ranges are rejected.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-015: Combined filters

**Requirement**: FR-5 — Filters
**Technique**: Equivalence Partitioning (single filter, combined filters, no-match combination)
**Priority**: High
**Preconditions**: TC-009 search executed.

**Test Data**:

| # | Filters                                  | Expected hotels          |
| - | ---------------------------------------- | ------------------------ |
| a | Stars ≥ 4                                | H-002, H-003, H-004      |
| b | Stars ≥ 4 + amenity **Pool**              | H-002, H-004             |
| c | Stars ≥ 4 + **Pool** + **Parking**        | H-004                    |
| d | Guest rating ≥ 8.5                        | H-002, H-004             |
| e | Property type **Hostel**                  | H-005                    |
| f | Stars 5 + property type **Apartment**     | none                     |

**Test Steps**:

| Step | Action                                    | Expected Result                                         |
| ---- | ----------------------------------------- | ------------------------------------------------------- |
| 1    | Apply filters (a) and check the list       | Exactly the expected hotels                             |
| 2    | Apply (b)–(e) one by one                   | Filters combine with **AND**; list matches the table    |
| 3    | Apply (f)                                  | Empty state with a **Clear filters** action             |
| 4    | Click **Clear filters**                    | All 5 hotels are shown again                            |

**Expected Result**: Filters are combined with AND logic, results match the seed data, and empty results show a helpful empty state.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-016: Sort results by each option

**Requirement**: FR-6 — Sort
**Technique**: Equivalence Partitioning (one value per valid sort option + invalid option)
**Priority**: Medium
**Preconditions**: TC-009 search executed (5 hotels).

**Test Data / Expected order**:

| # | Sort option              | Expected order                           |
| - | ------------------------ | ---------------------------------------- |
| a | Price: low to high       | H-005, H-001, H-002, H-003, H-004        |
| b | Price: high to low       | H-004, H-003, H-002, H-001, H-005        |
| c | Guest rating             | H-004, H-002, H-001, H-003, H-005        |
| d | Distance from center     | H-001, H-005, H-002, H-003, H-004        |
| e | Popularity               | H-004, H-002, H-001, H-003, H-005        |
| f | API `sort=foo` (invalid) | `422`, or default order with no error page |

**Test Steps**:

| Step | Action                                  | Expected Result                     |
| ---- | --------------------------------------- | ----------------------------------- |
| 1    | Select each sort option (a)–(e)          | Order matches the table             |
| 2    | Apply filter Stars ≥ 4, then sort by (a) | H-002, H-003, H-004 (sorting keeps the filter) |
| 3    | Call the API with (f)                    | Handled gracefully as described     |

**Expected Result**: Each sort option returns the expected order and keeps active filters.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-017: Hotel detail page for existing and non-existing hotel

**Requirement**: FR-7 — Hotel detail
**Technique**: Equivalence Partitioning (existing ID, non-existing ID, malformed ID)
**Priority**: Medium
**Preconditions**: Seed hotel `H-002` with 3 photos and 2 reviews.

**Test Data**: `H-002`; non-existing ID `000000000000000000000000`; malformed ID `abc`.

**Test Steps**:

| Step | Action                                         | Expected Result                                                        |
| ---- | ---------------------------------------------- | ---------------------------------------------------------------------- |
| 1    | From results, open `H-002`                     | Detail page shows name, photos (3), description, amenities (Wi-Fi, Pool), location/map, guest reviews (2) |
| 2    | Open the detail URL with the non-existing ID   | "Hotel not found" page with a link back to search; API `404`          |
| 3    | Open the detail URL with `abc`                 | Same "Hotel not found" page; API `404` or `422`, never `500`          |

**Expected Result**: Existing hotels show complete information; invalid IDs are handled without server errors.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 3. Price Comparison and Redirect

### TC-018: Provider prices from fresh cache and no availability

**Requirement**: FR-8 — Price comparison (BR-09)
**Technique**: Decision Table (DT-1 rules R1 and R3)
**Priority**: High
**Preconditions**: Hotel `H-002`; dates `TODAY+7` → `TODAY+9`. Cache for `P-01` written **14 minutes ago** with price 1500. `P-02` stub mode `NO_AVAILABILITY`. `P-03` stub mode `OK` (1550).

**Test Steps**:

| Step | Action                                         | Expected Result                                               |
| ---- | ---------------------------------------------- | ------------------------------------------------------------- |
| 1    | Open the `H-002` detail page                   | Comparison table lists the providers                          |
| 2    | Check `P-01` row                               | Shows 1500 from cache; the `P-01` stub received **0 calls** (R1) |
| 3    | Check `P-02` row                               | Shows "Not available for these dates"; no **View deal** button (R3) |
| 4    | Check `P-03` row                               | Shows 1550 with **View deal**                                |

**Expected Result**: Fresh cache is used without calling the provider; unavailable providers are shown but cannot be selected.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-019: One provider fails, others still shown

**Requirement**: FR-8; NFR Reliability
**Technique**: Decision Table (DT-1 rule R4)
**Priority**: High
**Preconditions**: Hotel `H-002`; empty cache. `P-01` stub `TIMEOUT`, `P-02` stub `ERROR_500`, `P-03` stub `OK` (1550).

**Test Steps**:

| Step | Action                                   | Expected Result                                         |
| ---- | ---------------------------------------- | ------------------------------------------------------- |
| 1    | Open the `H-002` detail page             | Page loads (does not wait indefinitely for `P-01`)      |
| 2    | Check the comparison table               | Only `P-03` is listed with 1550; `P-01` and `P-02` are omitted |
| 3    | Check the search results card for `H-002` | Lowest price shown is 1550                             |

**Expected Result**: Provider failures do not break the page; remaining providers are shown.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-020: Stale cache triggers a live price refresh

**Requirement**: FR-8, FR-15 (price feeds) — BR-09
**Technique**: Decision Table (DT-1 rule R2) with cache-age boundary
**Priority**: Medium
**Preconditions**: Hotel `H-002`. Cache for `P-01` written **15 minutes ago** with price 1500; `P-01` stub `OK` now returns 1450.

**Test Steps**:

| Step | Action                                     | Expected Result                                      |
| ---- | ------------------------------------------ | ---------------------------------------------------- |
| 1    | Open the `H-002` detail page               | `P-01` stub receives exactly 1 call                  |
| 2    | Check `P-01` row                           | Shows **1450** (live price)                          |
| 3    | Check the cache entry for `P-01`           | Price 1450 and timestamp updated to now              |
| 4    | Reload the page within 1 minute            | Still 1450; stub receives no new call (cache is fresh) |

**Expected Result**: A cache of 15 minutes or more is refreshed; a fresh cache avoids new provider calls.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-021: All providers fail

**Requirement**: FR-8; NFR Reliability and Usability
**Technique**: Decision Table (DT-1 rule R5)
**Priority**: High
**Preconditions**: Hotel `H-002`; empty cache; all provider stubs in `ERROR_500`.

**Test Steps**:

| Step | Action                         | Expected Result                                                        |
| ---- | ------------------------------ | ---------------------------------------------------------------------- |
| 1    | Open the `H-002` detail page   | Hotel information (photos, description, reviews) is displayed          |
| 2    | Check the comparison section   | Message "Prices are temporarily unavailable. Please try again later."; no **View deal** buttons |
| 3    | Check browser console / API    | API responds `200` with an empty price list (or `503` only for the prices endpoint); no unhandled errors |

**Expected Result**: The page degrades gracefully when no prices are available.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-022: Redirect to the selected provider

**Requirement**: FR-9 — Redirect to provider
**Technique**: Equivalence Partitioning (available provider vs unavailable provider)
**Priority**: High
**Preconditions**: Hotel `H-002`; `P-03` stub `OK`; `P-02` stub `NO_AVAILABILITY`; search `TODAY+7` → `TODAY+9`, 2 guests, 1 room.

**Test Steps**:

| Step | Action                                         | Expected Result                                                    |
| ---- | ---------------------------------------------- | ------------------------------------------------------------------ |
| 1    | Click **View deal** on `P-03`                  | A new tab opens the `P-03` URL                                     |
| 2    | Inspect the URL                                | Contains the provider's hotel ID, check-in, check-out, guests and rooms of the search |
| 3    | Check `P-02` row                               | No **View deal** button (cannot redirect to an unavailable deal)   |

**Expected Result**: The user is redirected to the chosen provider with the search parameters preserved.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 4. Map, Favorites and History

### TC-023: Map shows the same hotels as the result list

**Requirement**: FR-10 — Map view
**Technique**: Equivalence Partitioning (hotels with and without coordinates)
**Priority**: Low
**Preconditions**: TC-009 search executed. `H-005` has **no coordinates**.

**Test Steps**:

| Step | Action                                       | Expected Result                                         |
| ---- | -------------------------------------------- | ------------------------------------------------------- |
| 1    | Switch to **Map view**                        | Map centered on Guadalajara                             |
| 2    | Count markers                                | 4 markers (`H-001`–`H-004`); `H-005` is listed but without a marker, no error |
| 3    | Click the `H-002` marker                      | Popup with name and price; link opens the detail page   |
| 4    | Apply filter Stars ≥ 4                        | Markers update to `H-002`, `H-003`, `H-004`             |

**Expected Result**: Markers stay in sync with the result list and filters; missing coordinates do not break the map.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-024: Add and remove favorites

**Requirement**: FR-11 — Favorites
**Technique**: Equivalence Partitioning (add new, add duplicate, remove, anonymous)
**Priority**: Medium
**Preconditions**: User `U-01` with no favorites.

**Test Steps**:

| Step | Action                                                    | Expected Result                                     |
| ---- | --------------------------------------------------------- | --------------------------------------------------- |
| 1    | Logged out, click the ♥ on `H-002`                         | Prompt to log in; nothing is saved                  |
| 2    | Log in as `U-01`, click ♥ on `H-002` and `H-004`           | Hearts become filled                                |
| 3    | Call `POST /favorites` again for `H-002`                   | No duplicate (`200`/`409`); list still has 2 items  |
| 4    | Open **My favorites**                                      | Shows `H-002` and `H-004`                           |
| 5    | Remove `H-002`, reload the page                            | Only `H-004` remains (persisted)                    |
| 6    | Log in as `U-02` and open **My favorites**                 | Empty list (favorites are per user)                 |

**Expected Result**: Favorites are per user, persisted, and free of duplicates.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-025: Search history limit and re-run

**Requirement**: FR-12 — Search history (BR-07: last 10)
**Technique**: Boundary Value Analysis (10th and 11th search)
**Priority**: Low
**Preconditions**: User `U-01` logged in with an empty history.

**Test Data**: 11 searches for `Guadalajara` with check-in `TODAY+1` … `TODAY+11` (2 nights, 2 guests, 1 room). Search #1 is the oldest.

**Test Steps**:

| Step | Action                                       | Expected Result                                         |
| ---- | -------------------------------------------- | ------------------------------------------------------- |
| 1    | Run searches #1–#10, open **Recent searches** | 10 entries, newest first; #1 still present (max kept)   |
| 2    | Run search #11, open **Recent searches**      | Still 10 entries; #11 at the top; #1 evicted            |
| 3    | Click search #5 in the history                | Search form is filled with #5 values and results load   |

**Expected Result**: History keeps exactly the 10 most recent searches and re-runs them with the original criteria.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 5. Reviews

### TC-026: Review rating boundaries

**Requirement**: FR-13 — Reviews (BR-06: rating 1–5)
**Technique**: Boundary Value Analysis
**Priority**: Medium
**Preconditions**: Logged in as `U-04` (no reviews); use a different hotel per accepted row (`H-001`, `H-003`) so BR-06's one-review rule does not interfere.

**Test Data**: rating 0 ❌, 1 ✅, 5 ✅, 6 ❌ (text: "Great location and friendly staff.")

**Test Steps**:

| Step | Action                                         | Expected Result                                    |
| ---- | ---------------------------------------------- | -------------------------------------------------- |
| 1    | In the UI, try to submit without selecting stars (0) | "Select a rating from 1 to 5"                 |
| 2    | Submit rating 1 on `H-001` and rating 5 on `H-003` | Both reviews are published                      |
| 3    | Call the API with rating 0 and 6 (and 3.5)      | `422` for each                                     |

**Expected Result**: Only integer ratings 1–5 are accepted.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-027: Review text length boundaries

**Requirement**: FR-13 — Reviews (BR-06: 10–1000 characters)
**Technique**: Boundary Value Analysis
**Priority**: Medium
**Preconditions**: Logged in as `U-04`; rating 4; seed state reset after TC-026; a different hotel for each accepted row (`H-001`, `H-004`).

**Test Data**: text length 9 ❌ (`"Too short"`), 10 ✅ (`"Nice room!"`), 1000 ✅, 1001 ❌. Leading/trailing spaces are trimmed before counting.

**Test Steps**:

| Step | Action                              | Expected Result                                             |
| ---- | ----------------------------------- | ----------------------------------------------------------- |
| 1    | Submit text of 9 characters          | Rejected: "Review must be 10–1000 characters"               |
| 2    | Submit 10 and 1000 characters        | Published; full text displayed                              |
| 3    | Submit 1001 characters               | Rejected (UI counter blocks it; API `422`)                  |
| 4    | Submit `"   Too short   "`           | Rejected (trimmed length is 9)                              |

**Expected Result**: Only texts of 10–1000 characters (after trimming) are accepted.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-028: Review lifecycle: submit, edit, delete

**Requirement**: FR-13 — Reviews
**Technique**: State Transition (ST-1 transitions 1, 2, 3, 7)
**Priority**: Medium
**Preconditions**: `U-01` logged in; no review by `U-01` on `H-004`.

**Test Steps**:

| Step | Action                                                | Expected Result                                           |
| ---- | ----------------------------------------------------- | --------------------------------------------------------- |
| 1    | Submit rating 4, text "Very clean and quiet rooms." on `H-004` | State **Published**; review visible on the detail page; average rating updated |
| 2    | Edit it to rating 5, text "Excellent stay, would return." | Still **Published**; new text and rating shown; "edited" label |
| 3    | Delete the review and confirm                         | State **Deleted**; no longer visible; average rating recalculated |
| 4    | Call `PUT /reviews/{id}` and `DELETE /reviews/{id}` again | `404 Not Found` for both                               |

**Expected Result**: Valid transitions update the visible review and rating; a deleted review cannot be edited or deleted again.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-029: Review permissions for anonymous and non-author users

**Requirement**: FR-13 — Reviews (BR-06)
**Technique**: Decision Table (DT-2 rules R1, R2, R5)
**Priority**: High
**Preconditions**: Review `RV-01` by `U-02` exists on `H-002`. `U-01` has review `RV-02` on `H-002`.

**Test Steps**:

| Step | Action                                                         | Expected Result                                     |
| ---- | -------------------------------------------------------------- | --------------------------------------------------- |
| 1    | Logged out, open `H-002`                                       | Reviews are readable; **Write a review** prompts login (R1) |
| 2    | Logged out, call `POST /hotels/H-002/reviews`                  | `401`                                               |
| 3    | As `U-01`, check `RV-01` in the UI                             | No Edit/Delete buttons                              |
| 4    | As `U-01`, call `PUT` and `DELETE` on `RV-01`                  | `403` for both; `RV-01` unchanged (R2)              |
| 5    | As `U-01`, submit another review on `H-002`                    | Rejected `409`: "You already reviewed this hotel" (R5) |

**Expected Result**: Only authenticated users can review, only authors can modify their reviews, and each user has at most one review per hotel.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-030: Review persists after logout and server restart

**Requirement**: FR-13 — Reviews
**Technique**: State Transition (ST-1 state persistence)
**Priority**: Medium
**Preconditions**: `U-01` logged in; no review by `U-01` on `H-003`.

**Test Steps**:

| Step | Action                                          | Expected Result                              |
| ---- | ----------------------------------------------- | -------------------------------------------- |
| 1    | Submit rating 3, text "Average breakfast, good bed." on `H-003` | Review **Published**          |
| 2    | Log out and reopen `H-003`                       | Review still visible                         |
| 3    | Restart the backend (`docker compose restart backend`) and reopen `H-003` | Review still visible with the same data |
| 4    | Log in again as `U-01`                           | Edit/Delete available on that review         |

**Expected Result**: Review state is stored in the database, not in memory or the session.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 6. Admin

### TC-031: Admin creates, updates and deletes a hotel

**Requirement**: FR-14 — Hotel management
**Technique**: Equivalence Partitioning (valid form, missing required fields, invalid stars)
**Priority**: High
**Preconditions**: Logged in to `/employee/` as admin `U-03`.

**Test Data**:

| # | Name               | City         | Stars | Lat / Lng            | Expected            |
| - | ------------------ | ------------ | ----- | -------------------- | ------------------- |
| a | `QA Test Hotel`    | Guadalajara  | 3     | 20.6767 / −103.3475  | ✅ Created           |
| b | *(empty)*          | Guadalajara  | 3     | 20.6767 / −103.3475  | ❌ "Name is required" |
| c | `QA No Location`   | *(empty)*    | 3     | *(empty)*            | ❌ "Location is required" |
| d | `QA Bad Stars`     | Guadalajara  | 6     | 20.6767 / −103.3475  | ❌ "Stars must be 1–5" |

**Test Steps**:

| Step | Action                                                       | Expected Result                                        |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------ |
| 1    | Create hotels (b), (c), (d)                                  | Each rejected with the message in the table; nothing saved |
| 2    | Create hotel (a) with one image                              | Saved; appears in the admin list                       |
| 3    | In the client portal, search Guadalajara                     | `QA Test Hotel` appears in results                     |
| 4    | Edit (a): stars 4, add amenity Pool                          | Changes visible in admin list and client detail page   |
| 5    | Delete (a) and confirm                                       | Removed from admin list and from client search; detail URL returns "Hotel not found" |

**Expected Result**: Full CRUD works for valid data and invalid forms are rejected with field-level messages.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-032: Admin route access control

**Requirement**: FR-14, FR-15; NFR Security (RBAC)
**Technique**: Decision Table (DT-3 rules R1–R4)
**Priority**: High
**Preconditions**: Users `U-01` (user) and `U-03` (admin). An expired admin token and a tampered token (one character changed) are prepared.

**Test Data**: Endpoint `POST /admin/hotels` with valid hotel (a) from TC-031; page `/employee/`.

**Test Steps**:

| Step | Action                                        | Expected Result                                 |
| ---- | --------------------------------------------- | ----------------------------------------------- |
| 1    | Call the endpoint with **no token** (R1)       | `401`; opening `/employee/` redirects to login  |
| 2    | Call with the **expired** and the **tampered** token (R2) | `401` for both                       |
| 3    | Call with `U-01`'s valid token (R3)            | `403 Forbidden`; nothing created                |
| 4    | Log in to `/employee/` as `U-01`               | Access denied message; no admin data visible    |
| 5    | Call with `U-03`'s valid token (R4)            | `201 Created`                                   |

**Expected Result**: Only valid admin tokens can reach admin features; all other combinations are blocked.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-033: Admin moderates (removes) a review

**Requirement**: FR-15 — Review moderation; FR-13
**Technique**: State Transition (ST-1 transitions 4 and 6) and DT-2 rule R4
**Priority**: Medium
**Preconditions**: Review `RV-01` by `U-02` on `H-002` in state **Published**.

**Test Steps**:

| Step | Action                                                    | Expected Result                                       |
| ---- | --------------------------------------------------------- | ----------------------------------------------------- |
| 1    | As admin `U-03`, try to edit the text of `RV-01` via API   | `403` (admins moderate, they do not rewrite reviews)  |
| 2    | As admin, remove `RV-01` from the moderation screen        | State **Removed**; disappears from the `H-002` page; average rating recalculated |
| 3    | As `U-02`, try to edit `RV-01`                             | Rejected (`404`/`409`); review stays removed          |
| 4    | As `U-02`, open own profile/reviews                        | `RV-01` shown as removed by moderation (or not listed) |

**Expected Result**: Admins can remove inappropriate reviews; removed reviews cannot be edited back by the author.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 7. Error Handling and Security

### TC-034: Network error during search

**Requirement**: NFR Usability (clear errors, loading indicators)
**Technique**: Equivalence Partitioning (offline / request timeout)
**Priority**: Medium
**Preconditions**: Client portal loaded; DevTools available.

**Test Steps**:

| Step | Action                                                         | Expected Result                                         |
| ---- | -------------------------------------------------------------- | ------------------------------------------------------- |
| 1    | Set DevTools network to **Offline**, run the TC-009 search      | Loading indicator, then "Check your internet connection" with a **Retry** button |
| 2    | Set network back to **Online**, click **Retry**                 | Results load normally                                   |
| 3    | Throttle so the request exceeds the client timeout             | Same friendly error; no infinite spinner                |

**Expected Result**: Network failures show a recoverable error state and never a blank page.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-035: Server error during search

**Requirement**: NFR Usability
**Technique**: Equivalence Partitioning (HTTP 5xx partition)
**Priority**: Medium
**Preconditions**: Ability to force the search endpoint to return `500` (stop MongoDB container or use a test flag).

**Test Steps**:

| Step | Action                                             | Expected Result                                          |
| ---- | -------------------------------------------------- | -------------------------------------------------------- |
| 1    | Stop MongoDB (`docker compose stop mongo`), run a search | Message "Something went wrong on our side. Please try again." |
| 2    | Inspect the API response body                       | Generic JSON error; **no stack trace, query or internal details** |
| 3    | Start MongoDB again, retry                          | Search works                                             |

**Expected Result**: Server errors are shown as friendly messages and do not leak internals.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-036: Injection and XSS payloads are rejected or sanitized

**Requirement**: NFR Security (input validation and sanitization)
**Technique**: Equivalence Partitioning (malicious input partition) + error guessing
**Priority**: High
**Preconditions**: `U-01` exists; logged in for the review step.

**Test Data**:

| # | Field                | Payload                                                  |
| - | -------------------- | -------------------------------------------------------- |
| a | Login (API JSON)     | `{"email": "client1@example.com", "password": {"$ne": null}}` |
| b | Destination          | `{"$gt": ""}`                                            |
| c | Review text          | `<script>alert('xss')</script> Nice place to stay`       |
| d | Destination          | `<img src=x onerror=alert(1)>`                           |

**Test Steps**:

| Step | Action                                   | Expected Result                                                     |
| ---- | ---------------------------------------- | ------------------------------------------------------------------- |
| 1    | Send login (a)                           | `401` or `422`; **no session created** (NoSQL operator not executed) |
| 2    | Search with (b) via API                  | `422` or treated as plain text (no results); never returns all hotels |
| 3    | Submit review (c), reload the hotel page | Text is displayed escaped as plain text; **no alert** pops up       |
| 4    | Search with (d) in the UI                | Shown as text in the "no results" message; **no alert**             |

**Expected Result**: Malicious inputs never change query logic or execute in the browser.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —
