# Room Types, Physical Inventory & Pricing — HotelTrivago

Defines the hotel's room catalog, static pricing structure, physical room distribution, and the exact mathematical model for the 10% overbooking rule. Aligned with [`tests/data/test-data.md`](../../tests/data/test-data.md).

---

## 1. Room Categories Catalog (Seed Data)

All prices are static, quoted in **MXN per night**, and include taxes. Clients book by **Category ID** (`R-001` to `R-005`), never by physical room number.

| Category ID | Name | Room Type | Max Guests | Bed Configuration | Amenities | Price / Night (MXN) | Physical Rooms ($N$) | Max Reservations ($\lfloor N \times 1.1 \rfloor$) |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: |
| **R-005** | Single | `Single` | 1 | 1 Single Bed | Wi-Fi | $450 | 10 | 11 |
| **R-001** | Standard Double | `Double` | 2 | 1 Queen Bed | Wi-Fi | $1,000 | 20 | 22 |
| **R-002** | Deluxe Double | `Double` | 4 | 2 Double Beds | Wi-Fi, Balcony | $1,500 | 10 | 11 |
| **R-003** | Junior Suite | `Suite` | 4 | 1 King Bed + Sofa Bed | Wi-Fi, Minibar | $2,000 | 10 | 11 |
| **R-004** | Master Suite | `Suite` | 4 | 1 King + 2 Singles | Wi-Fi, Balcony, Minibar | $2,500 | 10 | 11 |
| **Total** | | | | | | | **60 Units** | **66 Bookings** |

> **QA Alignment Note:** `R-002` (Deluxe Double) is seeded with exactly **3 photos** to satisfy test case `TC-017`.

---

## 2. Physical Room Inventory Mapping

Booking Staff assign clients to specific physical rooms at check-in, and Cleaning Staff track housekeeping state per physical unit.

| Floor | Physical Room Numbers | Assigned Category | Count ($N$) | Upgrade Hierarchy Rank |
| :---: | :--- | :--- | :---: | :---: |
| **Floor 1** | `101` – `110` | `R-005` (Single) | 10 | 1 (Lowest) |
| **Floor 2** | `201` – `220` | `R-001` (Standard Double) | 20 | 2 |
| **Floor 3** | `301` – `310` | `R-002` (Deluxe Double) | 10 | 3 |
| **Floor 4** | `401` – `410` | `R-003` (Junior Suite) | 10 | 4 |
| **Floor 5** | `501` – `510` | `R-004` (Master Suite) | 10 | 5 (Highest) |

---

## 3. Overbooking & Upgrade Rules

### 3.1 The 10% Overbooking Formula
For any given date $d$ and Room Category $C$ with $N_C$ physical units not Out-of-Order:

$$\text{Max Allowed Reservations}(C, d) = \lfloor N_C \times 1.10 \rfloor$$

- Example: `R-001` has $N = 20$ physical rooms (`201`–`220`). The system accepts up to $20 \times 1.1 = 22$ active reservations for `R-001` on any given night.
- Once 22 rooms of `R-001` are booked for date $d$, `R-001` is excluded from search results for date Ranges overlapping $d$.

### 3.2 Collision Upgrade Path
When a client arrives for check-in and all $N$ physical rooms of their booked category are occupied (due to the 10% overbooking buffer), Booking Staff must assign an available physical room from the next highest rank in the **Upgrade Hierarchy**:

$$\text{R-005} \rightarrow \text{R-001} \rightarrow \text{R-002} \rightarrow \text{R-003} \rightarrow \text{R-004}$$

- **Price Protection:** The client pays the original nightly rate of the category they reserved, even when upgraded to a higher-tier room.

### 3.3 Virtual Room Object
The hotel operates a **virtual room** abstraction for each room-type reservation before a real physical room is assigned. A virtual room contains:
- Room category / type (`R-001` etc.)
- Date range for the booking
- A `virtual_reserved` array with one entry for each reserved day that has not yet been consumed or expired
- Number of guests and room count
- Charge amount and current status (`active`, `partially_converted`, `expired`, `converted`, `cancelled`)

A virtual room is paid for at booking time. To assign a client whose booking contains `N` reserved days, the client must be physically present and the selected physical room must be available for at least those same `N` consecutive stay dates. Room assignment is check-in: the system immediately consumes and converts that day's entry, which is not refundable even if the client leaves that day. On each subsequent stay day, it converts only that day's matching entry. The active `virtual_reserved` array shrinks by that one entry while the booking and its other reserved days remain. The booking record and history are retained as days are consumed.

The booking is `partially_converted` while it has both converted stay days and active reserved-day entries. It becomes `converted` after all reserved days are consumed during the stay. If the client departs early, remaining unused reserved days are refunded under `unused_day_refund_rate` and removed from the active array; they do not expire and the stay ends as an early departure.

### 3.4 Virtual Room Expiration & Date Rebooking
- Refund and rebooking rates are application-level configuration values, not system constants. Admins may change them freely if the backend lead implements the rate-management feature. Because of its complexity, the backend lead may instead omit that feature; in that case, the application uses the defaults below. The defaults remain application constants and are not system constants.
- Before check-in, if a reserved date passes without conversion to a real room, only that day's entry expires; the booking and its other reserved days remain active.
- Once the client has checked in, non-expired days start becoming used. If the client departs early, refund the unused days at `unused_day_refund_rate`.
- An expired virtual room may be reassigned to another date for `expired_day_rebooking_rate` times the day rate for the moved dates.
- Rebooking a **non-expired** virtual room is not allowed because the reservation still covers an active date range; shifting it would create a gap in active coverage.
- A free date change is allowed only when the reservation is **1 day before check-in**.
- A date change for an expired virtual room is cheaper than creating a new booking because it reuses the original reservation and only charges the date-change fee.

### 3.5 Refund Split Rules for Virtual Room Days
The application uses separate rates for refunds of unused and expired virtual-room days, and a separate rate for rebooking expired days. Their default assignments are `unused_day_refund_rate = 70%`, `expired_day_refund_rate = 50%`, and `expired_day_rebooking_rate = 120%`. These defaults apply unless changed by the admin-management feature described above.

| Scenario | Application variable |
| :--- | :--- |
| Refund for expired days, including days lost through late cancellation or late arrival | `expired_day_refund_rate` |
| Refund for unused, non-expired days, including early departure | `unused_day_refund_rate` |
| Rebooking an expired day | `expired_day_rebooking_rate` |

The refund amount is computed from the applicable rate and the lost or unused virtual-room day value. The rebooking rate is a charge multiplier, not a refund percentage.

### 3.6 Check-In, Check-Out & Room Availability
- Default check-in window: **3:00 PM–10:00 PM**. The operating day closes at **10:00 PM**.
- Default check-out window: **7:00 AM–1:00 PM**. The operating day opens at **7:00 AM**.
- Admins can change the check-in/out windows and operating-day opening/closing times.
- If the client has not checked out by the end of the check-out window, Booking Staff may charge an extra night manually. The system does not make this charge automatically.
- A physical room becomes assignable only when the current stay has checked out **and** the room is clean. An occupied room is not assignable even if cleaning is complete, and a checked-out but unclean room is not assignable.

---

## 4. Reservation Pricing & Refund Examples

### 4.1 Guest Capacity
For a reservation in one room category, the total guest capacity must be at least the number of guests:

$$\text{max\_guests} \times \text{rooms} \ge \text{guests}$$

For a reservation containing multiple room categories, capacity is the sum of each category's `max_guests` multiplied by the number of rooms booked in that category, and that total must be at least `guests`. The existing reservation limits of 1–5 rooms and `rooms <= guests` remain in force.

### 4.2 Standard Total Calculation
$$\text{Total Reservation Price} = \sum_{i=1}^{k} \left(\text{Price}_{\text{Category}_i} \times \text{Nights}\right)$$
Where $k$ is the number of rooms booked ($1 \le k \le 5$) and $1 \le \text{Nights} \le 30$.

### 4.3 Payment Capture & Refund Scenarios (Example: 4 Nights in `R-002` @ $1,500/night = $6,000 MXN)

| Scenario | Timing / Event | Amount Charged | Amount Refunded | Net Paid by Client |
| :--- | :--- | :---: | :---: | :---: |
| **Early Cancellation** | Cancelled $\ge 1$ day before Check-in | $0 (Not captured) | $0 (Full void) | **$0 MXN** |
| **Late Cancellation** | Cancelled on Check-in day (4 nights lost) | $6,000 | $3,000 ($6,000 × `expired_day_refund_rate`) | **$3,000 MXN** |
| **Late Check-in** | Client arrives 2 days late (uses 2 of 4 nights) | $6,000 | $1,500 (2 × $1,500 × `expired_day_refund_rate`) | **$4,500 MXN** |
| **Early Departure** | Client leaves after 3 nights (1 night lost) | $6,000 | $1,050 ($1,500 × `unused_day_refund_rate`) | **$4,950 MXN** |
| **Normal Stay** | Client completes all 4 nights | $6,000 | $0 | **$6,000 MXN** |

---

## 5. Room Dirtiness & Housekeeping Timing

The cleanliness lifecycle is related to occupancy: an occupied room is never in a clean state. It is `dirty` or `currently_cleaning`; it becomes clean only after check-out and cleaning completion.

| Condition | Dirtiness Rule | Configurable By Admin |
| :--- | :--- | :--- |
| **Unoccupied room** | A room remains clean until it has been vacant for **10 days**. After that threshold, it becomes `dirty` automatically. | Yes (`dirty_after_days`) |
| **Occupied room** | Once a stays begins, the room becomes `dirty` within the same day. | No (hardcoded) |
| **Room in cleaning** | A room may be `currently_cleaning` while still occupied. If the client checks out at the same time cleaning finishes, it can become clean and available immediately. | No |
| **Cleaned room** | A room is marked `cleaned` only after it is unoccupied; it is eligible for assignment only if check-out is complete. | No |

This model allows a `room_status` history to include combinations such as `occupied + dirty`, `occupied + currently_cleaning`, and `available + cleaned` without forcing vacancy before housekeeping work begins. Assignability requires both completed check-out and a clean room; cleanliness alone does not release an occupied room.