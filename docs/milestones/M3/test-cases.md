# Test Cases — HotelTrivago

**Milestone**: M3 — Black Box Testing
**Author**: Gilberto Anaya Mercado (QA Lead)
**Last updated**: 2026-11-01
**Total test cases**: 23

---

## Conventions

- **Test data** (users `U-xx`, rooms `R-xxx`) is defined in [`tests/data/test-data.md`](../../../tests/data/test-data.md).
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
| TC-013 | Search with missing or invalid fields                  | FR-4        | EP        | High     |
| TC-014 | Price range filter boundaries                          | FR-5        | BVA       | High     |
| TC-015 | Combined filters                                       | FR-5        | EP        | High     |
| TC-016 | Sort results by each option                            | FR-6        | EP        | Medium   |
| TC-017 | Room detail page for existing and non-existing room    | FR-7        | EP        | Medium   |
| TC-018 | Admin creates, updates and deletes a room              | FR-14       | EP        | High     |
| TC-019 | Admin route access control                             | FR-14       | DT        | High     |
| TC-020 | Network error during search                            | NFR-USA     | EP        | Medium   |
| TC-021 | Server error during search                             | NFR-USA     | EP        | Medium   |
| TC-022 | Injection and XSS payloads are rejected or sanitized   | NFR-SEC     | EP        | High     |
| TC-023 | Session and new password persist after a restart       | FR-2, FR-3  | ST        | Medium   |

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
**Technique**: State Transition (ST-2: LoggedOut → LoggedIn → LoggedOut, invalid token reuse, expiry)
**Priority**: High
**Preconditions**: User `U-01` exists; browser has no session.

**Test Data**: `client1@example.com` / `Client1Pass`

**Test Steps**:

| Step | Action                                                  | Expected Result                                         |
| ---- | ------------------------------------------------------- | ------------------------------------------------------- |
| 1    | Open `/client/`, click **Log in**, enter credentials, submit | Logged in; header shows the user's email/name and **Log out** |
| 2    | Open **My account**                                     | Page loads (protected route accessible)                 |
| 3    | Copy the auth token / session cookie (DevTools)         | —                                                       |
| 4    | Click **Log out**                                       | Redirected to home; **Log in** is shown again           |
| 5    | Open **My account**                                     | Redirected to login                                     |
| 6    | Call `GET /auth/me` with the copied old token            | `401 Unauthorized` (token invalidated on logout)        |
| 7    | Log in again, wait until the token expires (short lifetime in the test config), open **My account** | Redirected to login; `GET /auth/me` returns `401` |

**Expected Result**: Valid transitions LoggedOut → LoggedIn → LoggedOut work; the old token cannot be reused after logout or expiry.

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

**Requirement**: FR-3 — Password reset (BR-06)
**Technique**: State Transition (ST-1: Issued → Used)
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

**Requirement**: FR-3 — Password reset (BR-06)
**Technique**: State Transition (ST-1 invalid transitions)
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
**Preconditions**: Seed rooms `R-001`–`R-005` loaded.

**Test Data**: Check-in `TODAY+7`; check-out `TODAY+9`; guests 2; rooms 1.

**Test Steps**:

| Step | Action                                    | Expected Result                                        |
| ---- | ----------------------------------------- | ------------------------------------------------------ |
| 1    | Open `/client/`                           | Search bar is visible on the home page                 |
| 2    | Enter the test data and click **Search**  | Loading indicator is shown while searching             |
| 3    | Observe the results page                  | 5 rooms (`R-001`–`R-005`); search bar still visible    |
| 4    | Check each result card                    | Name, room type, price per night and total for **2 nights**, photo |

**Expected Result**: The hotel's rooms are listed with prices for the selected dates.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-010: Check-in date and stay length boundaries

**Requirement**: FR-4 — Search (BR-02, BR-03)
**Technique**: Boundary Value Analysis
**Priority**: High
**Preconditions**: Same as TC-009. Guests 2, rooms 1.

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
**Preconditions**: `TODAY+7` → `TODAY+9`, rooms 1.

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
**Preconditions**: `TODAY+7` → `TODAY+9`.

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

### TC-013: Search with missing or invalid fields

**Requirement**: FR-4 — Search; NFR Usability (error messages)
**Technique**: Equivalence Partitioning (invalid partitions)
**Priority**: High
**Preconditions**: Dates `TODAY+7` → `TODAY+9`, guests 2, rooms 1; each row changes one field.

**Test Data**:

| # | Field          | Value        | Partition    |
| - | -------------- | ------------ | ------------ |
| a | Check-in       | *(empty)*    | Missing      |
| b | Check-out      | *(empty)*    | Missing      |
| c | Guests (API)   | `two`        | Not a number |
| d | Check-in (API) | `2026-13-45` | Invalid date |

**Test Steps**:

| Step | Action                         | Expected Result                                                              |
| ---- | ------------------------------ | ---------------------------------------------------------------------------- |
| 1    | Search with (a) and (b)        | Not submitted; message "Select check-in and check-out dates"                 |
| 2    | Call the API with (c) and (d)  | `422` with a message naming the field; never `500`                           |

**Expected Result**: No crash or blank page; each partition shows a clear, actionable message.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-014: Price range filter boundaries

**Requirement**: FR-5 — Filters (BR-05: inclusive bounds, `0 ≤ min ≤ max`)
**Technique**: Boundary Value Analysis
**Priority**: High
**Preconditions**: TC-009 search executed. Per-night prices: `R-005` 450, `R-001` 1000, `R-002` 1500, `R-003` 2000, `R-004` 2500.

**Test Data**:

| # | Min  | Max  | Expected rooms       | Boundary                     |
| - | ---- | ---- | -------------------- | ---------------------------- |
| a | 1500 | 2000 | R-002, R-003         | Both prices on the bounds (inclusive) |
| b | 1500 | 1999 | R-002                | Max − 1 excludes R-003       |
| c | 1501 | 2000 | R-003                | Min + 1 excludes R-002       |
| d | 1500 | 1500 | R-002                | min = max                    |
| e | 0    | 450  | R-005                | Min lower bound 0            |
| f | −1   | 1000 | — (rejected)         | Min − 1                      |
| g | 2000 | 1500 | — (rejected)         | min > max                    |

**Test Steps**:

| Step | Action                                           | Expected Result                                        |
| ---- | ------------------------------------------------ | ------------------------------------------------------ |
| 1    | Apply the price filter with row (a)              | Exactly the expected rooms; result count updates        |
| 2    | Repeat with rows (b)–(e)                         | Exactly the expected rooms for each row                 |
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

| # | Filters                                  | Expected rooms           |
| - | ---------------------------------------- | ------------------------ |
| a | Room type **Suite**                      | R-003, R-004             |
| b | Room type **Suite** + amenity **Balcony** | R-004                   |
| c | Amenity **Balcony**                      | R-002, R-004             |
| d | Room type **Single**                     | R-005                    |
| e | Room type **Single** + **Balcony**       | none                     |

**Test Steps**:

| Step | Action                                    | Expected Result                                         |
| ---- | ----------------------------------------- | ------------------------------------------------------- |
| 1    | Apply filters (a) and check the list       | Exactly the expected rooms                              |
| 2    | Apply (b)–(d) one by one                   | Filters combine with **AND**; list matches the table    |
| 3    | Apply (e)                                  | Empty state with a **Clear filters** action             |
| 4    | Click **Clear filters**                    | All 5 rooms are shown again                             |

**Expected Result**: Filters are combined with AND logic, results match the seed data, and empty results show a helpful empty state.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-016: Sort results by each option

**Requirement**: FR-6 — Sort
**Technique**: Equivalence Partitioning (one value per valid sort option + invalid option)
**Priority**: Medium
**Preconditions**: TC-009 search executed (5 rooms).

**Test Data / Expected order**:

| # | Sort option              | Expected order                           |
| - | ------------------------ | ---------------------------------------- |
| a | Price: low to high       | R-005, R-001, R-002, R-003, R-004        |
| b | Price: high to low       | R-004, R-003, R-002, R-001, R-005        |
| c | API `sort=foo` (invalid) | `422`, or default order with no error page |

**Test Steps**:

| Step | Action                                  | Expected Result                     |
| ---- | --------------------------------------- | ----------------------------------- |
| 1    | Select each sort option (a)–(b)          | Order matches the table             |
| 2    | Apply room type Suite, then sort by (b)  | R-004, R-003 (sorting keeps the filter) |
| 3    | Call the API with (c)                    | Handled gracefully as described     |

**Expected Result**: Each sort option returns the expected order and keeps active filters.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-017: Room detail page for existing and non-existing room

**Requirement**: FR-7 — Room detail
**Technique**: Equivalence Partitioning (existing ID, non-existing ID, malformed ID)
**Priority**: Medium
**Preconditions**: Seed room `R-002` with 3 photos.

**Test Data**: `R-002`; non-existing ID `000000000000000000000000`; malformed ID `abc`.

**Test Steps**:

| Step | Action                                         | Expected Result                                                        |
| ---- | ---------------------------------------------- | ---------------------------------------------------------------------- |
| 1    | From results, open `R-002`                     | Detail page shows name, photos (3), description, amenities (Wi-Fi, Balcony), price per night |
| 2    | Open the detail URL with the non-existing ID   | "Room not found" page with a link back to search; API `404`          |
| 3    | Open the detail URL with `abc`                 | Same "Room not found" page; API `404` or `422`, never `500`          |

**Expected Result**: Existing rooms show complete information; invalid IDs are handled without server errors.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 3. Admin

### TC-018: Admin creates, updates and deletes a room

**Requirement**: FR-14 — Room management
**Technique**: Equivalence Partitioning (valid form, missing required fields, invalid price)
**Priority**: High
**Preconditions**: Logged in to `/employee/` as admin `U-03`.

**Test Data**:

| # | Name               | Room type    | Price/night | Expected                         |
| - | ------------------ | ------------ | ----------- | -------------------------------- |
| a | `QA Test Room`     | Double       | 1200        | ✅ Created                        |
| b | *(empty)*          | Double       | 1200        | ❌ "Name is required"             |
| c | `QA No Type`       | *(empty)*    | 1200        | ❌ "Room type is required"        |
| d | `QA Bad Price`     | Double       | −1          | ❌ "Price must be greater than 0" |

**Test Steps**:

| Step | Action                                                       | Expected Result                                        |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------ |
| 1    | Create rooms (b), (c), (d)                                   | Each rejected with the message in the table; nothing saved |
| 2    | Create room (a) with one image                               | Saved; appears in the admin list                       |
| 3    | In the client portal, run the TC-009 search                  | `QA Test Room` appears in results                      |
| 4    | Edit (a): price 1300, add amenity Balcony                    | Changes visible in admin list and client detail page   |
| 5    | Delete (a) and confirm                                       | Removed from admin list and from client search; detail URL returns "Room not found" |

**Expected Result**: Full CRUD works for valid data and invalid forms are rejected with field-level messages.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

### TC-019: Admin route access control

**Requirement**: FR-14; NFR Security (RBAC)
**Technique**: Decision Table (DT-1 rules R1–R4)
**Priority**: High
**Preconditions**: Users `U-01` (user) and `U-03` (admin). An expired admin token and a tampered token (one character changed) are prepared.

**Test Data**: Endpoint `POST /admin/rooms` with valid room (a) from TC-018; page `/employee/`.

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

## 4. Error Handling and Security

### TC-020: Network error during search

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

### TC-021: Server error during search

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

### TC-022: Injection and XSS payloads are rejected or sanitized

**Requirement**: NFR Security (input validation and sanitization)
**Technique**: Equivalence Partitioning (malicious input partition) + error guessing
**Priority**: High
**Preconditions**: `U-01` and admin `U-03` exist.

**Test Data**:

| # | Field                | Payload                                                  |
| - | -------------------- | -------------------------------------------------------- |
| a | Login (API JSON)     | `{"email": "client1@example.com", "password": {"$ne": null}}` |
| b | Room ID (detail URL) | `{"$ne": null}`                                          |
| c | Room description (admin) | `<script>alert('xss')</script> Quiet room`           |
| d | Room name (admin)    | `<img src=x onerror=alert(1)>`                           |

**Test Steps**:

| Step | Action                                   | Expected Result                                                     |
| ---- | ---------------------------------------- | ------------------------------------------------------------------- |
| 1    | Send login (a)                           | `401` or `422`; **no session created** (NoSQL operator not executed) |
| 2    | Open the room detail with (b)            | `404` or `422`; never returns a room                                |
| 3    | As admin, save a room with (c) and (d), open it in the client portal | Text is displayed escaped as plain text; **no alert** pops up |

**Expected Result**: Malicious inputs never change query logic or execute in the browser.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —

---

## 5. State Persistence

### TC-023: Session and new password persist after a restart

**Requirement**: FR-2, FR-3 (BR-06)
**Technique**: State Transition (persistence in ST-1 and ST-2)
**Priority**: Medium
**Preconditions**: TC-007 executed (`U-02`'s password is `NewPass2024` and the link is used); `U-01` logged in, token copied.

**Test Steps**:

| Step | Action                                                  | Expected Result                             |
| ---- | ------------------------------------------------------- | ------------------------------------------- |
| 1    | Restart the backend (`docker compose restart backend`)  | Backend is up again                         |
| 2    | Call `GET /auth/me` with `U-01`'s token                 | `200`; the session is still valid           |
| 3    | Log in as `U-02` with `NewPass2024`, then `Client2Pass` | New password works; old one is rejected     |
| 4    | Open the used reset link again                          | Still "This link is invalid or has expired" |

**Expected Result**: Session and password state are stored persistently, not in server memory.

**Actual Result**: — | **Status**: Not Executed | **Tested By**: — | **Date**: —
