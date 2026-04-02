Good call. Let me update the master plan with everything we've discussed since the last update.
What all needs to go in:

Microservice architecture (already in doc from earlier)
Repository pattern
Shared Pydantic schemas in shared/
Async fire-and-forget logging
Retrieval service loads corpus directly from DB at startup
Redis roles clarified (cache, embeddings, rate limiting)
Session context split (Redis + pgvector)
ENUMs in DB mapped to GraphQL types
PgBouncer as future ADR
Single DB, data service as sole owner
