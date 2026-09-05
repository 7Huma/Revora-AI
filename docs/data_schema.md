# Data Schema & Models

This project now uses a single canonical SQLAlchemy 2.0 typed model module:

`backend/app/db/models.py`

## Tables

- `customers`
- `payments`
- `checkout_events`
- `subscriptions`
- `invoices`
- `recovery_cases`
- `interventions`

## Relationships

`Customer`
→ Payments / Checkout Events / Subscriptions / Invoices / Recovery Cases

`RecoveryCase`
→ many `Intervention` records

## Enumerations

- `RiskScoreCategory`
- `RootCauseCategory`
- `RecoveryCaseStatus`
- `CommunicationChannel`

## Important design decision

The database model is the source of truth for the rest of the system.

The next segments should build on these tables rather than creating duplicate model definitions.
