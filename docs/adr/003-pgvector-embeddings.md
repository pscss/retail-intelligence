# ADR 003 — pgvector for Embedding Storage

## Status
Proposed — not yet implemented

## Context
FAISS holds embeddings in memory — fast but not persistent or scalable.
Moving embeddings to pgvector keeps everything in one data store and
enables horizontal scaling of the retrieval service.

## Decision
Add pgvector extension to PostgreSQL. Store product and FAQ embeddings
in the database alongside their metadata.

## Schema changes
```sql
-- Add to products table
embedding VECTOR(384)

-- Add to faqs table
embedding VECTOR(384)

-- Add to session_queries table (see ADR 001)
query_embedding VECTOR(384)
```

## Migration strategy
1. Enable pgvector extension
2. Add vector columns via Alembic migration
3. Backfill embeddings via seed script
4. Update retrieval service to query pgvector instead of FAISS

## When to implement
After FAISS is working end to end. Swap in retrieval service only.
