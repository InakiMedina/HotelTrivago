# Business Rules Specification — HotelTrivago

This document formalizes all system constraints, booking mechanics, overbooking formulas, financial refund policies, and operational workflows. It combines the core operational rules with the validation boundaries established in M3 (`BR-01` through `BR-06`).

---

## 1. Authentication & Security Constraints

| Rule ID | Category | Specification |
| :--- | :--- | :--- |
| **BR-01** | Password Policy | Passwords must be **8 to 64 characters** long and contain at least one letter and one digit. Stored as `bcrypt` hashes (`$2b$`). |
| **BR-06** | Password Reset | Reset tokens are **single-use**, expire after **10 minutes**, and requesting a new token immediately invalidates all prior active tokens for that user. |
| **BR-07** | Email Uniqueness | User emails are unique and evaluated **case-insensitively** (`client1@example.com` == `CLIENT1@Example.com`). |
| **BR-08** | No Enumeration | Login and password reset endpoints must return identical neutral responses regardless of whether an email exists in the database. |

---

## 2. Search & Reservation Boundaries

| Rule ID | Category | Specification |
| :--- | :--- | :--- |
| **BR-02** | Check-in Date | Check-in date must be greater than or equal to `TODAY` (evaluated against server UTC/local configured date). |
| **BR-03** | Stay Duration | Stay duration (`check_out - check_in`) must be between **1 and 30 nights** inclusive. |
| **BR-04** | Party & Room Limits | A single reservation supports **1 to 10 guests** and **1 to 5 rooms**, with `rooms <= guests`. For one room category, capacity must satisfy `max_guests × rooms >= guests`. For multiple categories, the sum of `max_guests × rooms` for each category must be at least `guests`. Every booked category must have a defined `max_guests`. |
| **BR-05** | Price Filtering | Search price filters follow `0 <= min <= max` (MXN). Both `min` and `max` bounds are **inclusive**. |
| **BR-09** | Room Type Booking | Clients **cannot** select or reserve a specific physical room number (e.g., Room 204). Clients reserve **Room Categories/Types** (e.g., `R-001 Standard Double`). Multiple rooms can be bundled into a single reservation (up to 10 guests total). |

---

## 3. Overbooking & Room Assignment Mechanics

| Rule ID | Category | Specification |
| :--- | :--- | :--- |
| **BR-10** | 10% Overbooking Allowance | If the hotel has $N$ physical rooms of a given category (matching price and bed configuration) available on a target date, the system allows up to $\lfloor N \times 1.1 \rfloor$ (or $N \times 1.1$) reservations for that category across clients. |
| **BR-11** | Physical Assignment | **Booking Staff** assign a specific physical room number (e.g., `101`, `202`) during check-in, while the client is physically present. Room assignment and check-in are one action. |
| **BR-12** | Check-in & Departure | **Booking Staff** execute check-in and check-out. Check-out completes the stay and makes the room unoccupied, but the room is not assignable again until it is also clean. |
| **BR-13** | Collision & Upgrade Resolution | If overbooking (`BR-10`) or operational overlap causes a collision where no physical rooms of the reserved type are available at check-in, **Booking Staff** can reassign the client to a **higher-tier room type** at no extra cost to the client. |
| **BR-14** | Staff Override Authority | **Booking Staff** have full operational override to evict/remove guests from rooms, force a room switch (same type), or change a client's room category during an active stay. |

---

## 4. Payments, Captures, Virtual Rooms & Refund Policies

*Note: All payment processing is simulated internally; no real financial gateways are charged (`BR-19`).*

| Rule ID | Category | Specification |
| :--- | :--- | :--- |
| **BR-15** | Deferred Card Capture | Clients must register valid payment card details during reservation creation. However, the card is **not charged (captured) until 1 day (`check_in - 1 day`) before check-in**. |
| **BR-16** | Full Refund Window | A reservation is **100% refundable** (or voided prior to capture) if cancelled on or before `check_in - 1 day` (`cancellation_date <= check_in - 1 day`). |
| **BR-17** | Partial Refund by Day Type | For a cancellation after the full-refund deadline or a late arrival, lost/expired days are refunded at `expired_day_refund_rate`. For an early departure, unused, non-expired days are refunded at `unused_day_refund_rate`. A day consumed at check-in is not refundable, even if the client leaves that day. |
| **BR-25** | Virtual Room Booking | Clients do not reserve a physical room directly. They book a **virtual room** object that represents room-type availability for a given date range, type/category, and occupant count. Its `virtual_reserved` array contains one entry for each reserved day. |
| **BR-26** | Virtual-to-Real Conversion | Room assignment and check-in are the same action and require the client to be physically present. **Booking Staff** assigns the client only to a physical room available for at least the same `N` consecutive stay days. The system immediately consumes the check-in day's virtual entry and converts it to real occupancy; that day is not refundable. It then consumes only one matching virtual day per subsequent stay day, without deleting the booking or its other reserved days. |
| **BR-27** | Residual Virtual Days | Remaining unconsumed virtual days may be refunded when cancelled or when the client departs early. Early-departure days use `unused_day_refund_rate`; cancellation refunds use the rate applicable to each day's expired or non-expired status. Do not mark early-departure days expired. |
| **BR-28** | Expired Virtual Reservation | A reserved date expires only if it passes before the client checks in. Only that virtual day expires; other reserved days remain in the booking. Once the client checks in, no remaining day can expire; early-departure days are refunded instead. An expired virtual day may be moved to another date at `expired_day_rebooking_rate` times the original day rate. |
| **BR-29** | Refund and Rebooking Rates | The application uses `unused_day_refund_rate`, `expired_day_refund_rate`, and `expired_day_rebooking_rate`. Admins may change these application-level values if the backend lead implements rate management. Due to complexity, the backend lead may omit that feature; if omitted, the application uses the default values defined below. |
| **BR-30** | Date Rebooking Policy | A virtual room date may be changed to another date only when the booking is already **expired**. Rebooking a non-expired virtual room is not allowed because it creates a gap in active reservation coverage. |
| **BR-31** | Same-Day Date Change | A reservation can be moved to another date **1 day before check-in** without penalty or additional charge. |
| **BR-32** | Expired Date Change Pricing | Changing the date of an **expired** virtual room is cheaper than creating a completely new reservation because it reuses the original reservation value and applies only the rebooking charge (`expired_day_rebooking_rate` times the day rate). |
| **BR-33** | Occupancy and Cleanliness Constraints | An occupied room is never in a clean state; it is `dirty` or `currently_cleaning`. A room becomes clean only after the client checks out and cleaning completes. |
| **BR-34** | Dirty Room Timing | Unoccupied rooms become dirty only after the room has remained vacant for **10 days** (or the admin-configured threshold). Occupied rooms become dirty within the same day. |
| **BR-35** | Consecutive Room Availability | To assign a client with `N` reserved virtual days, the selected physical room must be available for at least those same `N` consecutive dates. |
| **BR-36** | Check-in / Check-out Windows | Default check-in is **3:00 PM–10:00 PM** and default check-out is **7:00 AM–1:00 PM**. The operating day opens at **7:00 AM** and closes at **10:00 PM**. Admins can change these times. |
| **BR-37** | Late Check-out Charge | If a client has not checked out by the configured end of the check-out window (default **1:00 PM**), Booking Staff may charge an extra night. The system does **not** apply this charge automatically. |
| **BR-38** | Room Reassignment Availability | A room is available for another client only after the current client has checked out and the room is clean. Checkout alone does not make an unclean room assignable; cleaning alone does not make an occupied room assignable. |

### Refund Calculation Formula (`BR-17`, `BR-29`)
$$\text{Refund Amount} = \sum_{\text{applicable days}} \left(\text{Nightly Rate} \times \text{Applicable Refund Rate}\right)$$

The application defaults are `unused_day_refund_rate = 70%`, `expired_day_refund_rate = 50%`, and `expired_day_rebooking_rate = 120%`. These are application-level values, not system constants. The first two are refund rates; the rebooking rate is a charge multiplier. Admins may change them if the rate-management feature is implemented. The backend lead may omit that feature due to its complexity, in which case the application uses these defaults.

### Virtual Room Rebooking Rule
- **Non-expired virtual room:** cannot be rescheduled because that would leave a date range without a reservation.
- **Expired virtual room:** can be reassigned to a new date at `expired_day_rebooking_rate` times the original virtual-day price.
- **1 day before check-in:** rescheduling is free and allowed as a same-day change.

---

## 5. Staff Management, Payroll & Housekeeping

| Rule ID | Category | Specification |
| :--- | :--- | :--- |
| **BR-18** | Admin Exclusivity | Only **Admins** can hire (create) new staff accounts, decrease or increase an existing staff member's salary, or fire (deactivate/delete) staff. |
| **BR-19** | Base Salary Inheritance | Newly hired staff automatically receive the current **Base Salary** configured for their specific role (`booking_staff` or `cleaning_staff`). |
| **BR-20** | Base Salary Decoupling | **Admins** can update the default Base Salary for a role at any time. A **decrease** in role base salary does **not** retroactively change the salaries of existing staff already hired at the previous base rate. |
| **BR-20A** | Base Salary Increase Effect | When the role base salary is increased, active employees whose salary is still tied to that base pay scale are also updated to the new base rate. |
| **BR-20B** | Employee Reduction Safety Floor | A manual reduction of an employee's individual salary is allowed only to the extent that it remains **at or above** the role's minimum salary floor (`role minimum salary`). The system blocks any attempt to reduce below that floor. |
| **BR-21** | Work Tracking & Audit | **Admins** can view logged worked hours and completed task metrics (check-ins processed, rooms cleaned) for every staff member. |
| **BR-22** | Automated Payroll | The system automatically calculates and disburses simulated payroll to **Booking Staff** and **Cleaning Staff** based on their active salary rate and logged hours. |
| **BR-23** | Housekeeping Workflow | **Cleaning Staff** can view a filtered queue of physical rooms requiring cleaning and transition their status between `needs_cleaning`, `currently_cleaning`, `cleaned`, and `dirty` while occupancy is tracked separately. |
| **BR-24** | Physical Locks Independence | Room lock mechanisms and physical keys operate outside the core web system and are handled independently at the front desk. |

---

## 6. Low Priority & Future Scope Rules

### Least Priority
- **Externalized Housekeeping:** The `cleaning_staff` portal functionality can be bypassed or handled outside the system if schedule constraints require descoping; Booking Staff/Admins would toggle room readiness directly.

### Possible Additions (Post-MVP)
- **Client Reviews & Ratings:** Clients can post ratings and text reviews for completed stays (currently descoped for M3 single-hotel MVP).
- **Stay Extensions & Upgrades:** Clients can request stay extensions or room type switches, executed strictly through the **Booking Staff** portal.
- **Simulated Smart Locks CLI:** A command-line interface (CLI) simulating IoT smart lock state transitions trigg
- **Robuste Cleaning Staff UI** A Cleaning Staff frontend with the option to post photos of found damage while entering a room and photos after cleaning