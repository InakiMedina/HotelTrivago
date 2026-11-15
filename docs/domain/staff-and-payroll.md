# Staff Roles, Salaries & Automated Payroll — HotelTrivago

Specifies the human resources rules, base salary configurations, work tracking metrics, and simulated payroll execution managed by Administrators.

---

## 1. Staff Roles & Base Salaries

All monetary values are in **MXN** and simulated within the platform.

| Role ID | Role Title | Default Base Hourly Rate (MXN) | Standard Weekly Hours | Default Bi-Weekly Base Pay (MXN) | Payroll Type |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `booking_staff` | Booking / Front Desk Staff | $120.00 / hr | 40 hrs | $9,600.00 | Automated |
| `cleaning_staff` | Housekeeping / Cleaning Staff | $90.00 / hr | 40 hrs | $7,200.00 | Automated |
| `admin` | System / Hotel Administrator | $200.00 / hr | 40 hrs | $16,000.00 | Exempt / Admin |

---

## 2. Salary Governance Rules

### 2.1 Hiring & Base Salary Inheritance
When an `admin` creates a new employee account:
1. The system looks up the current `base_hourly_rate` configured in the `role_configs` collection for the selected role (`booking_staff` or `cleaning_staff`).
2. That value is copied directly into the new employee's document (`employee.hourly_rate = role_config.base_hourly_rate`).

### 2.2 Global Base Salary Changes
When an `admin` updates the global Base Salary for a role:
- **Future Hires:** Any staff member hired after the update automatically starts at the new base rate.
- **Decreases to Base Salary:** Lowering the role's base salary does **not** retroactively alter employees already employed at the previous rate.
- **Increases to Base Salary:** Increasing the role's base salary **does** update the effective hourly rate for active employees whose compensation is still tied to that base scale.
- **Minimum Floor:** The system enforces a minimum salary floor equal to the role's configured minimum hourly rate. The admin cannot reduce any employee's pay below that minimum.

### 2.3 Individual Salary Adjustments
- An `admin` may increase an individual employee's `hourly_rate` at any time (`new_rate > current_rate`).
- An `admin` may also decrease an employee's `hourly_rate` to correct a manual salary-entry mistake, but only if the new value remains **greater than or equal to** the role minimum salary floor.
- Salary decreases are intentionally allowed by the system even though they are disfavored by the business; this is a controlled exception to support payroll corrections.
- Firing an employee sets their status to `terminated`, immediately revoking Employee Portal login access and halting future payroll cycles.

---

## 3. Work Tracking & Audit Metrics

Admins can view the following performance and attendance metrics per staff member:

| Role | Tracked Hours Field | Tracked Work Output Metrics | Triggering System Events |
| :--- | :--- | :--- | :--- |
| **Booking Staff** | `hours_worked` (logged per shift) | - `checkins_completed`; - `checkouts_completed`; - `room_assignments_made`; - `collisions_resolved` | Incremented automatically when staff executes check-in, check-out, room switch, or upgrade endpoints. |
| **Cleaning Staff** | `hours_worked` (logged per shift) | - `rooms_cleaned`; - `active_cleaning_tasks` | Incremented automatically when staff transitions a physical room from `currently_cleaning` to `cleaned`. |

---

## 4. Automated Simulated Payroll Calculation

At the end of each payroll period (or when triggered via the Admin payroll simulator endpoint), the system generates a `payroll_payout` record for every active `booking_staff` and `cleaning_staff` member:

$$\text{Gross Payout (MXN)} = \text{Employee.hourly\_rate} \times \text{Employee.hours\_worked\_in\_period}$$

Upon payout generation:
1. A simulated payment transaction (`status: "paid"`) is recorded in the `payroll_history` collection with timestamp, employee ID, hours worked, hourly rate snapshot, and total amount.
2. The employee's `hours_worked_in_period` counter resets to `0` for the new cycle while preserving cumulative lifetime hours (`total_lifetime_hours`).