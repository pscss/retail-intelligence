# ADR 005 — Performance Optimisations

## Status
Partially implemented — critical fixes applied, deferred items tracked here

## Context
Initial CRUD implementation prioritised correctness and readability over
performance. The following issues were identified during code review and
are tracked here for future implementation.

---

## Applied at implementation (not deferred)

### 1. Database indexes on filter columns
Added indexes on all columns used in WHERE clauses and ORDER BY:
- `products.department`
- `faqs.intent_label`
- `query_logs.operation`
- `query_logs.created_at`
- `query_logs.input_hash`

### 2. Bounded fetches on filtered endpoints
All "get all matching" endpoints (`get_by_intent`, `get_by_department`,
`get_by_operation`) now accept `limit` and `skip` parameters.

### 3. Combined count + fetch
Paginated list endpoints use a single query with `COUNT(*) OVER()` window
function instead of two separate queries.

---

## Deferred items

### 4. Bulk insert with RETURNING
**Problem:** `bulk_create()` refreshes each object individually in a loop,
adding one roundtrip per record.

**Solution:** Use SQLAlchemy `insert().returning()` for true bulk insert:
```python
