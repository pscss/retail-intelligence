# ADR 001 — Session Context Management

## Status
Proposed — not yet implemented

## Context
Users querying the API may ask follow-up questions that reference previous
queries in the same session. Without context, each request is stateless and
follow-up queries lose meaning.

## Decision
Session context will be split across two stores:
- Redis: active session state (hot, fast, TTL 30 minutes)
- pgvector: query embeddings per session (semantic, disk-based, daily cleanup)

## Schema (to be implemented)
```sql
