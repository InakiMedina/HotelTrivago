# Entities and Actions — HotelTrivago

Defines all user roles, system actors, portal access boundaries, and permitted actions across the platform.

---

## 1. Portal & Role Mapping

| Actor / Role | Role Identifier | Portal Access | Authentication Required |
| :--- | :--- | :--- | :--- |
| **Anonymous Visitor** | `anonymous` | Client Portal (`/client/`) | No |
| **Registered Client** | `user` | Client Portal (`/client/`) | Yes (JWT / Session) |
| **Booking Staff** | `booking_staff` | Employee Portal (`/employee/`) | Yes (JWT / Session) |
| **Cleaning Staff** | `cleaning_staff` | Employee Portal (`/employee/`) | Yes (JWT / Session) |
| **Administrator** | `admin` | Employee Portal (`/employee/`) | Yes (JWT / Session) |

---

## 2. Actions by Entity

### 2.1 Anonymous Visitor (`anonymous`)
- View available room categories/types, descriptions, photos, amenities, and static nightly prices (`FR-7`).
- Search room availability by check-in date, check-out date, guest count (1–10), and room count (1–5) (`FR-4`).
- Filter search results by price range (`min`/`max`), room type, and amenities (`FR-5`).
- Sort search results by price ascending or descending (`FR-6`).
- Register a new client account with email and password (`FR-1`).
- Log in to an existing client account (`FR-2`).
- Request a password reset email link and submit a new password via token (`FR-3`).

### 2.2 Registered Client (`user`)
*Inherits all Anonymous Visitor actions, plus:*
- Log out and invalidate active session token (`FR-2`).
- View **My Account** profile and reservation history.
- Register and update simulated payment card data.
- Create a **virtual room reservation** for one or more room types (up to 5 rooms / 10 guests total, subject to the $N \times 1.1$ overbooking cap).
- Pay for the booked virtual room at time of booking; it remains a virtual booking after room assignment, while the system converts and removes only one matching reserved day per stay day.
- Cancel an upcoming virtual room reservation:
  - Receive **100% refund** (voided capture) if cancelled at least 1 day prior to check-in.
  - Receive refund for remaining non-expired virtual days under the configured non-expired percentage (default **70%** of unused days).
  - Receive a different refund for expired virtual days under the configured expired percentage (default **50%** of expired days).
- Request early departure or late check-in adjustments (processed via Booking Staff, yielding a 50% refund on lost days; the consumed check-in day is not refundable).
- Submit a change-of-date request for an expired virtual room to a new date at **120%** of the original room-day price, or request a free same-day date change 1 day before check-in.

### 2.3 Booking Staff (`booking_staff`)
- Log in and log out via the Employee Portal (`/employee/`).
- View all client reservations (upcoming, active, cancelled, completed) and current physical room occupancy.
- Assign a client who is physically present and has sufficient valid **virtual room bookings** to a specific physical room number (e.g., `101`, `304`) only when that room is available for at least the same number of consecutive stay days; this assignment is the **Check-in** and must occur within the configured check-in window (default **3:00 PM–10:00 PM**).
- At check-in, the system consumes the current day's virtual entry and converts it into real occupancy; that day is not refundable, even if the client leaves that day. The system consumes only one matching virtual day per subsequent stay day, leaving the booking and its other reserved days intact.
- Handle late arrivals by expiring only reserved dates that passed before check-in and refunding lost days under the 50% partial-refund rule.
- Resolve overbooking collisions (`N * 1.1`) by upgrading the client to a higher-tier room type at no additional charge.
- Execute **Check-out / Departure** within the configured check-out window (default **7:00 AM–1:00 PM**); on early departure, refund remaining unused reserved days under the 50% partial-refund rule without expiring them.
- If a client has not checked out by the end of the configured check-out window, optionally charge an extra night manually; the system does not apply this charge automatically.
- Override active stays:
  - Switch a client from one physical room to another.
  - Change a client's assigned room category/type.
  - Evict/remove a client from a room (terminating the stay).
- Extend a client's stay duration upon request.
- Handle expired virtual-room rebooking requests by moving the reservation to a later date under the system's expired-room pricing rule.
- View personal logged hours, completed booking actions, and automated salary payouts.

### 2.4 Cleaning Staff (`cleaning_staff`)
*Note: Marked as lowest priority role; actions may be absorbed by Booking Staff/Admin if descoped.*
- Log in and log out via the Employee Portal (`/employee/`).
- View the list of physical rooms currently marked as `needs_cleaning`.
- Update physical room housekeeping status:
  - Mark room as `currently_cleaning` when starting work.
  - Mark cleaning complete; if the client remains, the room stays `occupied_dirty`, and if checkout completes at the same time, it becomes `available_clean`.
- Log worked hours / completed room cleanings.
- View personal automated salary payouts.

### 2.5 Administrator (`admin`)
- Log in and log out via the Employee Portal (`/employee/`).
- **Room Catalog CRUD (`FR-14`):**
  - Create new room categories/types with name, category, nightly price, amenities, description, and photos.
  - Update existing room category details, pricing, and physical inventory counts.
  - Delete room categories/types.
- **Staff & HR Management:**
  - Hire (create) new `booking_staff` and `cleaning_staff` accounts (automatically initialized with the role's current Base Salary).
  - Fire (deactivate/remove) staff members.
  - Increase or decrease the individual salary of specific staff members to correct payroll mistakes, while respecting the minimum salary floor.
  - Modify the global **Base Salary** for `booking_staff` or `cleaning_staff` roles.
  - Configure the system refund percentages for non-expired versus expired virtual-room cancellations and the dirty-room threshold.
  - Configure the check-in and check-out windows and the operating-day opening and closing times.
- **Audit & Payroll Oversight:**
  - View worked hours and work output metrics (check-ins, room assignments, rooms cleaned) for each employee.
  - Monitor and trigger the automated simulated payroll system for all active staff.
---

## 3. Role-Based Access Control (RBAC) Matrix

| Action / Endpoint Group | `anonymous` | `user` | `booking_staff` | `cleaning_staff` | `admin` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Search, Filter, Sort, View Rooms | ✅ | ✅ | ✅ | ✅ | ✅ |
| Register / Password Reset | ✅ | ✅ | ❌ | ❌ | ❌ |
| Book Room Type / Cancel Own Booking | ❌ | ✅ | ❌ | ❌ | ❌ |
| Assign Physical Room / Check-in / Check-out | ❌ | ❌ | ✅ | ❌ | ✅ |
| Evict Guest / Switch Room / Upgrade Collision | ❌ | ❌ | ✅ | ❌ | ✅ |
| View & Update Room Cleaning Status | ❌ | ❌ | 👁️ (View) | ✅ (Update) | ✅ |
| Room Type CRUD (`/admin/rooms`) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Hire / Fire Staff & Increase Individual Salary | ❌ | ❌ | ❌ | ❌ | ✅ |
| Modify Role Base Salary & View Staff Metrics | ❌ | ❌ | ❌ | ❌ | ✅ |


## 4. System Entities and Actions

### 4.1. Room Category (`room_type`)
- Create room category with name, category type, nightly price, description, amenities, and photos (Admin)
- Update category pricing, amenities, or description (Admin)
- Delete room category (Admin)
- Query available room categories matching dates, guest count, and room count (Client / Anonymous)
- Validate 10% overbooking capacity threshold ($\lfloor N \times 1.1 \rfloor$) for selected dates (System)

### 4.2. Physical Room Unit (`room_unit`)
- Initialize physical room numbers mapped to floors and categories (DB Seed / Admin)
- Assign a specific physical room number to a confirmed reservation during check-in, while the client is present (Booking Staff)
- Transition housekeeping status between `available`, `occupied`, `needs_cleaning`, `currently_cleaning`, and `cleaned`; a room is assignable only when checkout is complete and it is clean (Cleaning Staff / Booking Staff)
- Force room switch between physical units of the same category (Booking Staff)
- Escalate room category upgrade during collision overflow (Booking Staff)

### 4.3. Reservation (`reservation`)
- Create reservation bundling room categories, dates, guest count, and registered payment card (Client)
- Validate check-in date $\ge$ `TODAY`, stay length $1-30$ nights, and party limits ($1-10$ guests, $1-5$ rooms) (System)
- Calculate total nightly rate and apply deferred card capture schedule (`check_in - 1 day`) (System)
- Cancel reservation with 100% refund if $\ge 1$ day before check-in, or 50% refund on lost days if $< 1$ day or late/early departure (Client / System)
- Execute check-in during the configured check-in window and record physical room occupancy (Booking Staff)
- Execute check-out during the configured check-out window and queue unit for housekeeping; optionally charge an extra night manually for checkout after the window, with no automatic system charge (Booking Staff)
- Terminate stay via forced guest eviction (Booking Staff)

### 4.4. Payment (`payment`)
- Register and securely store simulated payment card data (Client)
- Authorize and schedule deferred card capture for 1 day prior to check-in (System)
- Execute simulated card charge capture at check-in minus 24 hours (System)
- Void authorization or process 100% / 50% refund transactions upon cancellation or shortened stay (System)

### 4.5. Staff Profile / Payroll Record (`staff_record`)
- Initialize employee account inheriting default role base salary for `booking_staff` or `cleaning_staff` (Admin)
- Update individual hourly rate or deactivate/terminate staff account (Admin)
- Modify global role base salary; decreases to the base salary do not alter active employee salaries, while increases do (Admin)
- Reduce an employee's salary only if the resulting value remains at or above the minimum salary floor for the role (Admin)
- Log shift hours worked and task outputs (check-ins processed, rooms cleaned) (System / Staff)
- Compute and disburse automated simulated payroll payouts based on hours worked and hourly rates (System / Admin)

### 4.6. Virtual Room Booking (`virtual_room_booking`)
- Create a virtual room request for a room type and date range (Client)
- Pay for the virtual room booking when the reservation is created (Client / System)
- Maintain the booking as a virtual object with a `virtual_reserved` array containing one entry per reserved day (Client / System)
- Require the assigned physical room to be available for at least the same number of consecutive stay days as the virtual booking (System / Booking Staff)
- Require the client to be physically present for room assignment, which is also check-in; immediately consume and convert that day's entry, which is not refundable (Booking Staff / System)
- On each subsequent stay day, convert only that day's virtual entry into real occupancy and remove only that entry from the active array (System)
- Refund unconsumed days when a reservation is cancelled before check-in under the applicable cancellation rule; after early departure, refund remaining unused days at 50% under BR-17, without expiring them (System)
- Before check-in, expire only a reserved-day entry whose date passes without conversion and allow that expired day to be rebooked at `120%` of its original rate (System / Booking Staff)
- After check-in, never expire remaining reserved days; refund them under the 50% partial-refund rule if the client departs early (System)
- Permit a free date change only when the reservation is 1 day before check-in (Client / Booking Staff)
- Reject date changes for non-expired virtual room bookings because the client must retain active reservation coverage for each date in the current stay (System)
