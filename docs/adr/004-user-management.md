# ADR 004 — User Management

## Status
Proposed — not yet implemented

## Context
dunnhumby's core value is personalisation. Tying inference requests to
user context enables behavioural analytics and personalised results over
time.

## Decision
Add user context to the data model without building full auth.

## Schema (to be implemented)
```sql
users (
    id          SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    segment     VARCHAR(100),
    created_at  TIMESTAMP
)

-- Add to query_logs
user_id INTEGER REFERENCES users(id)
```

## Notes
- external_id maps to retailer's own customer ID
- No password/auth built here — API key auth covers service-to-service
- Full OAuth2 is a separate ADR when multi-tenant support is needed

## When to implement
After core inference and retrieval services are working end to end.
