**PROJECT DELIVERY / 19 NOVEMBER 2026**

Hotel Management System Development Plan

Prepared for The Olive Branch Hotel, Port Harcourt

The first milestone is a complete stay on the hotel’s local network. Reception should be able to reserve one of the 20 rooms, verify payment, check a guest in and out, and print a receipt the accountant can trace. The restaurant, pool bar, room-service menu and public booking website will then use the same room, payment and stock records.

## Delivery milestones

| **Milestone**             | **Planning window** | **What the hotel can review**                                                                                                          |
|---------------------------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **Foundation**            | Week 1              | Site survey, room list, roles, signed operating rules and a working local installation with test data.                                 |
| **Front desk pilot**      | Weeks 2–3           | A supervised booking-to-checkout demonstration with room availability, payment verification and receipts.                              |
| **Integrated operations** | Weeks 4–6           | Outlet sales, QR orders, stock receipts, supplier purchases, maintenance and daily reports reconcile across desks.                     |
| **Website and opening**   | Weeks 7–8           | Public booking, outage handling, recovery rehearsal, staff training and supervised go-live. Allow weeks 9–10 for issues found on site. |

## Basis for planning

The ₦1,000,000 software package covers 16 modules, deployment, staff training, documentation, a perpetual hotel-use licence and six months of support from operational handover. Hardware, additional networking, domain and website hosting, internet and recurring cloud backup charges are budgeted separately.

The schedule is a working estimate for one full-time developer, an implementation partner available for site work and equipment testing, and hotel staff available for weekly acceptance. Week 1 starts at project readiness. Confirm the estimate after the site survey and review of any existing code. The earlier two-to-three-week target applies to the initial pilot.

**01 / FUNCTIONAL SCOPE**

# Guest stays and outlet operations

Use these numbers for requirements, issue tracking and hotel sign-off. A module is complete when staff can perform the task and verify its effect on the next department.

| **Module**                      | **Delivery commitment**                                                                                                             | **Acceptance example**                                                                                        |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| **01 Reservations**             | Calendar, dates and guests, booking source, group bookings, rates, seasonal overrides, deposits and cancellations.                  | Two users request the last room for overlapping dates. Only one obtains a valid hold.                         |
| **02 Front desk**               | Guest details, arrival and departure lists, room moves, upgrades, extensions, check-in, checkout and printable folios.              | Move a checked-in guest and extend the stay. Charges and receipt references follow the guest.                 |
| **03 Room management**          | Categories, features, prices, room history, occupancy, readiness and maintenance blocks. Staff update cleaning status manually.     | A clean occupied room and a vacant blocked room both remain unavailable for assignment.                       |
| **04 Outlet POS**               | Restaurant and pool-bar tills, menus, kitchen tickets or display, split bills, permissions, basic cashier opening and closing.      | Two drinks sold at the pool bar appear on one receipt, under the correct cashier and outlet.                  |
| **05 QR room service**          | Mobile menu, quantities, notes, item availability, stay validation and order routing to the existing kitchen queue.                 | An active guest submits one order. A repeated tap creates one kitchen ticket. Access expires at checkout.     |
| **06 Payments and billing**     | Cash, card-terminal and transfer records, split tenders, deposits, applied payments, refunds, balances and receipts.                | A verified deposit reduces the final balance exactly once. An unpaid folio blocks checkout.                   |
| **07 Inventory and stores**     | Stock by location, receipts, transfers, issues, damage, counts, expiry where applicable, low stock and configured sales deductions. | One carton of 12 bottles received, four transferred and two sold leaves eight in store and two at the outlet. |
| **08 Purchasing and suppliers** | Suppliers, requests, approvals, purchase orders, partial deliveries, supplier invoices and payment references.                      | Receiving six of ten ordered units adds six to stock and leaves four outstanding.                             |

**02 / FUNCTIONAL SCOPE**

# Management and booking channels

| **Module**                         | **Delivery commitment**                                                                                                    | **Acceptance example**                                                                                     |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| **09 Maintenance**                 | Fault tickets, priority, assignee, repair cost, history, preventive tasks and room blocking or release.                    | A serious fault removes a vacant room from availability. An authorised release restores eligibility.       |
| **10 Finance records**             | Operational revenue, advances, cashbook, expenses, payable references, categories and daily and monthly summaries.         | Accountant traces a daily revenue figure to room and outlet charges and reconciles collections separately. |
| **11 Dashboard**                   | Occupancy, arrivals, departures, in-house guests, sales, balances, stock alerts and rooms under repair.                    | Manager and owner can drill from an agreed daily figure to its permitted underlying detail.                |
| **12 Reports and exports**         | Revenue, occupancy, booking source, arrivals, outlet and cashier sales, stock, expenses, balances, maintenance and audit.  | A date-filtered Excel or PDF export matches the same period on screen. Access follows the user’s role.     |
| **13 Audit logs**                  | Searchable protected records for approvals, rate changes, voids, refunds, access and sensitive settings.                   | An investigator sees who approved a refund, when, why, and the original payment reference.                 |
| **14 Notifications**               | In-app alerts for arrivals, payments, overdue balances, stock thresholds, room readiness, maintenance and backup failures. | A low-stock event alerts the designated user once and records acknowledgement.                             |
| **15 Security and administration** | Individual users, permissions, session controls, configuration, encrypted backups, monitoring and tested recovery.         | A disabled account loses access. A separate test server restores a booking, payment and uploaded file.     |
| **16 Public booking website**      | Room photos, facilities, policies, prices, live availability, guest details and direct reservations linked to reception.   | A guest obtains a booking reference under the agreed payment policy. Reception sees the same booking.      |

## Scope baseline

The 18 November software bill adds the website to the 15 modules in the 17 November scope. Separate housekeeping scheduling, CRM, mobile check-in, automated WhatsApp, hotel-wide shift management and full double-entry accounting would require a scope change. An online payment gateway also requires a separate decision.

**03 / SYSTEM DESIGN**

# How the system runs

Proposed stack for the development team: Django with a REST API for hotel operations, PostgreSQL for records, and Next.js with TypeScript for browser screens. Build one backend with separate functional areas. Run the staff interface and its assets locally so reception can sign in and work when Starlink is unavailable.

| **Component**                      | **Placement and responsibility**                                                                                                                                                                                                            |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Hotel application and database** | Dedicated server, wired to the hotel network. Owns all room allocations, rates, guest stays, orders, payments, audit entries and stock movements. Local printer access and background tasks use this system.                                |
| **Staff and guest access**         | Staff use local HTTPS from reception, offices and both tills. Guest Wi-Fi allows access to the QR ordering route. Restrict other services and enforce permissions on each request at the server.                                            |
| **Public website**                 | Host public photos and information off site. A narrowly scoped booking service requests availability and holds through a secure connection initiated from the hotel. Keep hotel database credentials and staff interfaces inside the hotel. |
| **Background processing**          | Commit business changes first. Store pending notifications and print jobs durably, then retry by unique job reference. A failed printer or notification must leave the recorded payment available to reprint.                               |
| **Recovery storage**               | Use separate local media and a hotel-controlled off-site account for encrypted backups. Assign an alert recipient and separate recovery-key custodian.                                                                                      |

## When the website and reception want the last room

The website requests a time-limited hold from the local reservation service. In a database transaction, the service selects an eligible physical room and reserves its time interval. Both website and front desk use this same operation. The guest sees a reference only after the hotel records the result. A manager-configured expiry releases abandoned holds.

If a response is lost, the website retries with the same request ID and recovers the original outcome. If Starlink or the secure connection is down, the public site continues to show photos and hotel contact details, pauses live booking and invites the guest to contact reception. On reconnection it checks the outstanding request before accepting a retry.

**04 / BUILD SPECIFICATION**

# Data and transaction rules

| **Area**                    | **Core records and rules to implement**                                                                                                                                                                                                                                                  |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Rooms and reservations**  | RoomType, Room, RatePlan, Reservation, RoomAllocation, Stay and RoomBlock. Track cleanliness separately from occupancy. Use start-inclusive, end-exclusive intervals and a database overlap constraint for reserved or blocked room time. Preserve the rate quoted for an existing stay. |
| **Sales and payments**      | Folio, Charge, Payment, PaymentAllocation, Refund, Receipt, OutletOrder and OrderLine. Store monetary amounts in integer kobo and present NGN. Retain original transactions. Authorised reversals link back to them. One source charge can be posted only once.                          |
| **Stock and procurement**   | Item, UnitConversion, Store, StockMovement, Supplier, PurchaseOrder and GoodsReceipt. Transfer stock as paired movements. Each receipt or sale posts its movement once. Count differences require a reason and approval.                                                                 |
| **Operations and controls** | MaintenanceTicket, RoomStatusHistory, User, Role, Approval, AuditEvent and Notification. Record actor, time, reason and the affected record. Keep posted records and approvals beyond the lifetime of a staff account.                                                                   |

## Operating decisions for the first build

**Booking and settlement.** Proposed default pending hotel sign-off: a deposit or part payment can hold a reservation. Reception confirms it and checks the guest in once full required accommodation payment is verified. An expired hold releases the room, while any money received remains on record for resolution. Checkout requires zero outstanding balance.

**Outlet authority.** Reception verifies its own transfers and each outlet cashier verifies its own bank receipt or terminal reference. Record the bank terminal result without storing card credentials. Start outlet sales on immediate settlement. Enable room charges only after management approves eligibility, limits and final settlement.

**Financial reporting.** Store business dates in Africa/Lagos and timestamps consistently. Agree the day-close time with the accountant. Keep earned revenue, deposits, collections and refunds distinct. Define occupancy using eligible room-nights and report hourly stays separately when enabled.

**Access and privacy.** Reception handles stays, cashiers handle their outlet, stores users record stock, the accountant reconciles, the manager approves and the owner views reports. Privileged changes require named accounts and reasons. Restrict guest contact fields, exports, logs and backup access.

**05 / IMPLEMENTATION SEQUENCE**

# Stages 1 to 4

Build a complete, testable workflow at each stage. Use synthetic hotel records in development, then demonstrate the same workflow to a designated hotel reviewer.

## Stage 1 Readiness and foundation \| Week 1

Request the room register, sample tariff, menu, supplier list, opening stock, staff roles, receipt format and opening balances. Inspect any existing repository before estimating reuse. Survey Starlink handoff, Wi-Fi isolation, power, printers and local server. Agree who owns the website domain and backup account.

Create development and test environments, database migrations, named roles, access checks, protected audit events, build checks and a reproducible release package. Seed 20 fictional rooms, two outlets and sample users. Demonstrate a local login, permitted and denied screens, a database migration and a restore to a clean test instance.

## Stage 2 Rooms and reservations \| Week 2

Deliver the rooms board, booking calendar and shared availability service. Add hold expiry, cancellation, rate snapshots, group reservations, room assignments and blocks. Prototype the public connection using test data while the core reservation API takes shape.

Demonstrate that simultaneous requests cannot double-book. Check back-to-back stays, cleaning buffers, a move to a different room, a blocked room and an expiry. Record how reception resolves payments that arrive after expiry.

## Stage 3 Front desk and billing \| Week 3

Implement check-in, moves, extensions, deposit allocation, split settlement, refunds, checkout and receipt reprints. Run the pilot on reception equipment with a test guest. Print on the hotel’s actual printer, reconcile a shift sample and repeat a payment after a simulated timeout.

Pilot sign-off belongs to reception, the manager and the accountant. Use a supervised rehearsal until access controls, backup recovery and the hotel’s live-use decision are documented. Record remaining functions and the release to which each belongs.

## Stage 4 Restaurant, pool bar and room service \| Week 4

Set up both tills, menu pricing, kitchen tickets, cashier opening and closing and a stock-movement interface. Generate room QR codes backed by stay-bound access. Route guest orders through the same order service as till entries. Exercise an unavailable item, duplicate submission, approved void and receipt reprint at both outlets.

**06 / IMPLEMENTATION SEQUENCE**

# Stages 5 to 8

## Stage 5 Stock, purchasing and maintenance \| Week 5

Configure stores and units, import an approved opening count, and finish sale deductions, transfers, counts and adjustments. Connect purchase approval to partial delivery and stock receipt. Implement faults, assignment, repair costs, preventive schedules and authorised room release.

Stores signs off one purchase through receipt, transfer and sale. The manager signs off one blocked room, including what reception must do if it already has a future allocation. The system must flag the conflict and retain the reassignment trail.

## Stage 6 Finance, reporting and management \| Week 6

Build cashbook, operating expenses, supplier references and daily summaries on posted transactions. Publish dashboards, Excel/PDF reports and in-app notifications. Implement date and outlet filters plus owner view-only access. Run a sample business day with the accountant and trace discrepancies down to individual source records.

## Stage 7 Public booking website \| Week 7

Publish approved photography, room descriptions, rates, policies and contact details on the hotel’s domain. Connect live search, hold, guest details and confirmation to the tested reservation service. Display payment instructions agreed by the hotel and a clear pending-payment status. Assign pending web bookings to reception and show the booking source.

Test on a phone outside guest Wi-Fi. Race a website request against reception, interrupt the connection after a reservation is recorded, expire an abandoned hold and reconnect. The manager checks the guest-facing messages and confirms that each outcome matches reception’s record.

## Stage 8 Site acceptance and handover \| Weeks 8–10

Finish printer tests, guest-network isolation, production backups and a measured restore. Import approved master data and openings, deliver role-based training, then run a supervised shift. The manager and accountant review the acceptance evidence on the following pages before deciding whether to open each channel.

## How to track delivery

Maintain a backlog by module and stage. Each ticket names the user, business rule, acceptance example, dependency and reviewer. A completed ticket includes the working screen or report, relevant tests, migration or configuration notes and a demonstration. Review scope changes and their effect on price or dates before scheduling them.

**07 / VERIFICATION**

# Acceptance tests for opening

Run these scenarios against a production-like installation with both tills and the intended printers. Keep the input records, expected and actual results, reviewer and date for each test.

| **Test and reviewer**                   | **Passing result**                                                                                                                                                                                                                                 |
|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Last room • Reception**               | Submit overlapping desk and website requests together. Exactly one allocation succeeds. Cancellation or expiry makes the room available again.                                                                                                     |
| **Guest account • Accountant**          | For an illustrative ₦60,000 stay, record a ₦20,000 deposit and a verified ₦40,000 balance. After the stay is earned, room revenue and total receipts are each ₦60,000, the folio is zero and the two payments remain visible.                      |
| **Outlet and stock • Cashier / stores** | Sell two ₦1,500 drinks from ten bottles. The till records ₦3,000 once and stock becomes eight. Retrying or reprinting changes neither total. A receipt reprint keeps its original reference.                                                       |
| **Refund and permissions • Manager**    | A cashier requests a refund and an authorised approver records a reason. The original sale remains traceable. Accountant verifies the refund and whether stock should return based on physical disposition.                                        |
| **Guest QR • Outlet supervisor**        | Complete an order for an active stay, then check out. An old room link cannot place an order against the next guest. Staff screens and guest records stay inaccessible from guest Wi-Fi.                                                           |
| **Finance and export • Accountant**     | Record an expense, an outstanding supplier invoice and an advance. Dashboard, Excel and PDF reconcile to the signed source totals for the same business date and outlet.                                                                           |
| **Outage and recovery • Partner**       | Disconnect Starlink. Local login, stay, cash sale and local QR order work on the powered LAN. Public bookings pause. Restart services, reconnect and restore to spare hardware. Compare recovered records and attachments with the recovery point. |
| **Load and usability • Technical lead** | Proposed target for review: with five staff stations active plus a website and QR session, 95% of local availability reads and till saves complete within two seconds, excluding printer time. Record actual measurements on site.                 |

## Release decision

Stop rollout for duplicate bookings or payments, unresolved cash discrepancies, a failed restore, incorrect access to guest records or an unusable critical desk. Assign other defects an owner and a retest date. The manager approves operations, the accountant approves reconciliation and the technical lead records the release version.

**08 / INSTALLATION AND CONTINUITY**

# Site rollout and recovery

## Fit the installation to the equipment schedule

The equipment bill provides one dedicated server, three desktops and monitors, two POS computers, two receipt printers, one office printer, five workstation UPS units and two 1 TB backup drives. The partner maps each device to a desk and verifies wired server access, guest and staff Wi-Fi separation, printer drivers, server/network power protection and measured UPS runtime before live use.

## Prepare the live records

Use controlled import templates for rooms, rates, menu items, pack sizes, suppliers and opening stock. Reception confirms future reservations and in-house stays at cutover. The accountant signs opening deposits, unpaid supplier references and opening floats. Dry-run imports first, compare counts and values, then lock the approved opening snapshot.

## Backups and recovery drill

Proposed targets from the hosting plan are a database recovery point every 15 minutes, a nightly base backup plus files and configuration, weekly disconnected drive rotation and a monthly restore exercise. Retain 30 daily and 12 month-end copies if storage and hotel policy permit. For PostgreSQL, test the base backup and continuous transaction-log chain together. Encrypt copies and keep recovery keys separately.

Monitor the age of both the last local and last off-site recovery points. Queue encrypted uploads during a Starlink outage and alert on overdue backups or low disk space. On spare equipment restore the application version, database and matching files. Time the exercise and record actual data loss exposure before agreeing a recovery-time target.

## Cut over and fall back safely

Before opening, take a verified backup, record the release and stock/cash opening figures, check the website connection and print a test receipt at each till. Start with a nominated receptionist and cashier. Check the first booking, outlet sale and end-of-shift totals with the accountant.

If a release fails before live transactions, roll back the release and opening configuration. After live entries exist, pause affected writes, preserve their records and reconcile them before any restore. During a server outage, use numbered manual slips, designate one person to allocate rooms, then enter and cross-check each slip exactly once. Resume public sales only after reception validates room availability.

**09 / OWNERSHIP AND NEXT ACTIONS**

# First sprint and handover

| **Owner to nominate**                                       | **Immediate responsibility**                                                                                                  | **Handover evidence**                                                                |
|-------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Delivery lead • Shine Bright Universal Services Limited** | Own the backlog, application build, demonstrations, defect resolution and release decisions with the hotel.                   | Source/release package, configuration guide, migration history and known-issues log. |
| **Implementation partner**                                  | Inspect the site, map terminals and printers, configure network and power protection, test backups and train a local contact. | Device map, printer outputs, restore drill and access handover.                      |
| **Manager and owner**                                       | Approve rates, cancellation and discount rules, website copy, access permissions and room-charge policy.                      | Signed policy decisions, content approval and operational acceptance.                |
| **Reception, outlet leads and accountant**                  | Supply master data and opening figures. Rehearse check-in, sale, refund, export and day-close using named accounts.           | Signed opening totals, role-based training record and reconciled sample shift.       |

## The first five working days

**Day 1** Walk through a booking, a pool-bar sale and checkout with the staff who perform them. Decide the deposit threshold, short-stay rules, web-hold expiry and who can approve refunds. Record unresolved questions with owners.

**Day 2** Inventory hardware and existing code. Obtain the 20-room register, tariffs, menu, units, receipt format and domain contact. Agree the pilot’s pass criteria and revise effort estimates.

**Day 3** Set up the repository, environment instructions, PostgreSQL migrations, named test users, audit baseline and automatic checks. Seed the test hotel.

**Day 4** Build the first reception view with availability and room holds. Run concurrent requests for the same room against the database.

**Day 5** Demonstrate the working reservation slice, local restart and first restore. Agree the Week 2 backlog with reception and the accountant.

## After operational handover

Record the handover date and six-month support end date. Give the hotel a support contact, escalation route, role guides and recovery contacts. Log incidents by business impact. Agree response expectations, monitoring ownership and a monthly restore review. At support close, review open faults and agree any ongoing maintenance separately.
