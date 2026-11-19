# OLIVE-BRANCH project rules

Follow the [development plan](docs/development-plan.md). Work only on the stage explicitly requested. Do not build ahead.

## Architecture

- Use one Django backend with Django REST Framework and PostgreSQL. Use Next.js with TypeScript for the frontend.
- Organize the backend into separate Django apps by functional area: `rooms`, `reservations`, `frontdesk`, `billing`, `outlets`, `roomservice`, `inventory`, `purchasing`, `maintenance`, `finance`, `reports`, `audit`, `notifications`, `accounts`, and `booking_gateway`.
- The entire staff UI, including its assets and sign-in, must work on the local network without internet access.

## Data and transactions

- Store monetary amounts as integer kobo. Never use floating-point values for money. Display amounts in NGN.
- Determine business dates in `Africa/Lagos` and store timestamps in UTC.
- Represent room time as start-inclusive, end-exclusive intervals. Enforce non-overlap for reservations and room blocks on the same room with a PostgreSQL exclusion constraint.
- Never edit or delete posted transactions. Record reversals as separate transactions linked to the original.
- Require a client request ID as an idempotency key for every write that can be retried. A retry with the same key must recover the original outcome without duplicating the write.

## Permissions and audit

- Enforce permissions on the server for every request.
- Record an `AuditEvent` for every privileged action. Include the actor, time, reason, and affected record.

## Tests

- Ship tests with every feature.
- Run both backend and frontend tests before finishing each task.
- After every push, check the GitHub Actions run for that commit. If it fails, fix it and push again before reporting done. The human does not run tests manually.
