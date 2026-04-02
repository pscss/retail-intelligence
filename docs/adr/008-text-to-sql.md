# ADR 008 — Text-to-SQL for Natural Language Analytics

## Status
Proposed — not yet implemented

## Context
The sentiment-trend endpoint currently uses hardcoded SQL queries.
A natural extension is letting business users query the analytics
layer in plain English without needing to know SQL or the schema.

Example user query:
"Which products had declining sentiment this week?"
"How many complaints were triaged as HIGH severity yesterday?"
"What are the top 5 most queried product categories?"

## Decision
Add a Text-to-SQL layer between the user and PostgreSQL.

## Architecture
```
User natural language query
        ↓
Gateway /v1/retail/analytics endpoint
        ↓
Text-to-SQL service
  - Schema context injected into prompt
  - LLM generates SQL (Claude API or local model)
  - SQL validated before execution
        ↓
PostgreSQL (read-only connection)
        ↓
Result formatted + explained by LLM
        ↓
Response to user
```

## Schema context strategy
The LLM needs to know the schema to generate correct SQL.
Inject a minimal schema description into every prompt:
```
Tables available:
- query_logs(id, operation ENUM, input_hash, result_label,
  confidence, latency_ms, served_from, created_at)
- products(id, product_id, commodity_desc, department, created_at)
- faqs(id, question, answer, intent_label, created_at)
- task_registry(id, name, model, is_active)

Only SELECT queries are allowed.
Always include a LIMIT clause.
```

## Production risks and mitigations

| Risk | Mitigation |
|---|---|
| SQL injection via generated query | Whitelist SELECT only. Reject any query containing INSERT/UPDATE/DELETE/DROP |
| Schema hallucination | Inject exact schema into every prompt. Validate table/column names before execution |
| Expensive queries (full table scans) | Enforce LIMIT 1000 max. Add query timeout (5 seconds). Sandbox on read replica |
| Wrong results returned confidently | Always return the generated SQL alongside the result so users can verify |
| PII exposure | query_logs stores hashes not raw text — safe. Products/FAQs are corpus data — safe |

## Implementation plan
1. Add POST /v1/retail/analytics to gateway
2. Build text_to_sql service in gateway/services/
3. Inject schema context + user query into LLM prompt
4. Parse and validate generated SQL (sqlparse library)
5. Execute on read-only DB connection
6. Format result + include generated SQL in response

## Model choice
- Claude API (claude-haiku-4-5) — fast, cheap, strong SQL generation
- Local model (SQLCoder-7B) — no data leaves infrastructure, GDPR-safe
- Recommendation: local SQLCoder for production (GDPR), Claude API for demo

## Interview line
> "The trend endpoint uses predefined queries today. The natural
> extension is Text-to-SQL — a business user asks 'which products
> had declining sentiment this week' in plain English and the system
> generates and runs the query. That requires guardrails: schema
> validation, SELECT-only sandboxing, query timeouts, and returning
> the generated SQL so users can verify the answer. It's on the
> roadmap — the data infrastructure we've built today supports it
> without changes."

## When to implement
After core services are deployed and working end to end.
Treat as a Day 4 stretch goal or post-interview project.
