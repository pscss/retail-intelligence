# ADR 002 — PgBouncer Connection Pooling

## Status
Proposed — not yet implemented

## Context
SQLAlchemy's built-in connection pool handles demo scale. At dunnhumby
production scale (millions of requests), PostgreSQL's default connection
limit becomes a bottleneck.

## Decision
Add PgBouncer as a connection pooler between all services and PostgreSQL.

## Architecture
```
Services → PgBouncer :6432 → PostgreSQL :5432
```

## Configuration
- Pool mode: transaction (most efficient)
- Max client connections: 1000
- Max server connections: 20

## When to implement
Day 3 production hardening phase.
