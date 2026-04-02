RETAIL INTELLIGENCE API

dunnhumby Final Round — Master Plan Document

Prateek Singhal  |  April 2026  |  v0.1.0-dev

# 0. The Brief (verbatim)

You need to stand up an inference API for a transformer model. It will have a variety of tasks it can perform, and users will want to be able to query these easily. How would you do this? What are the key considerations to account for? Please produce a workplan that will take approximately five minutes to talk through, with another five for questions. You can present using any format you like, e.g. slides, text file, notebook etc. You will be asked to explain and justify your decisions. The question is deliberately a little underspecified — please answer as seems most sensible to you.

# 1. Strategic Framing

## What they're actually testing

Can you make architectural decisions and justify them?

Do you understand production ML beyond notebooks?

Can you think in systems, not just models?

Do you know what you don't know and how to handle it?

## Our angle

We are not building a demo. We are building a production-grade microservice platform and then explaining how it would scale. The demo is proof. The explanation is the interview.

## The one-line narrative (memorise this)

I scoped this as a production-grade microservice, not a prototype. Multiple transformer architectures serve different task types, routed through a single API surface with a retrieval layer for grounding in business data. Here's a live demo — then let me walk you through the decisions.

# 2. Architecture Decisions

## 2.1 Why multiple models?

| Model | Architecture | Best at | Tasks in our API |
| --- | --- | --- | --- |
| distilbert-base-uncased-finetuned-sst-2-english | Encoder (BERT family) | Classification | Sentiment |
| cross-encoder/nli-MiniLM2-L6-H768 | Cross-encoder NLI | Zero-shot classification | Intent, Triage |
| all-MiniLM-L6-v2 | Bi-encoder sentence transformer | Semantic similarity | Search, RAG |

Different transformer architectures are optimised for fundamentally different tasks. Encoder models like DistilBERT are efficient for classification because they see the full sequence bidirectionally. Cross-encoder NLI models enable zero-shot classification — new labels at inference time, no retraining. Bi-encoder sentence transformers produce fixed-size embeddings you can index for retrieval.

## 2.2 Why microservices over a monolith?

Each service has one responsibility — inference, retrieval, data management are fundamentally different scaling problems

Add or remove tasks without touching other services — new model = new service + new GraphQL mutation, nothing else changes

Independent scaling — inference is GPU-bound, retrieval is memory-bound, data service is IO-bound

Fault isolation — retrieval service going down does not kill sentiment analysis

Adding a task means adding a service and a GraphQL mutation — you don't touch inference, retrieval, or the DB schema. Removing a task means setting is_active = false in the task registry. The gateway reads that at startup. This is the operational flexibility a team actually needs.

## 2.3 Why GraphQL at gateway, REST internally?

GraphQL: clients ask for exactly what they need — a category manager and a data scientist hit the same API but get different shaped responses

GraphQL: single endpoint (/graphql) replaces 8 REST endpoints — cleaner for internal teams

REST internally: inter-service calls have known, fixed shapes — GraphQL overhead adds complexity with no benefit

REST internally: simpler, faster, easier to debug between services

## 2.4 Why inference is a GraphQL Mutation, not a Query?

Inference consumes compute resources, gets logged to the query_log table, and has side effects. GraphQL convention is correct here — queries are safe and idempotent, mutations are not. This also lets us apply different rate limiting and caching rules per operation type.

## 2.5 Why REST over gRPC for internal services?

Discoverability (Swagger/OpenAPI comes free with FastAPI)

Easier to debug and test during development

gRPC is the right call at 10k+ RPS — worth adding as a second transport layer at scale

## 2.6 Why FastAPI?

Native async support — critical for inference latency

Automatic OpenAPI/Swagger docs at /docs

Pydantic schemas enforce input validation for free

Production-proven at scale (Netflix, Uber, etc.)

## 2.7 Why FAISS over a cloud vector DB?

Zero infrastructure cost, zero latency overhead for demo scale

Identical conceptual pattern to Pinecone/Weaviate — the interview story holds

At scale: swap FAISS for Pinecone/Weaviate, keep all other code identical

In-memory is acceptable for a corpus of <10k documents

## 2.8 Single DB — data service as sole owner

One PostgreSQL instance, four services. But only the data service connects to it directly.

| Service | DB access | How it gets data |
| --- | --- | --- |
| Data Service | Direct PostgreSQL connection | ORM via SQLAlchemy |
| Inference Service | None | No DB needed |
| Retrieval Service | None at runtime | Loads corpus from data service at startup via HTTP |
| Gateway | None | Calls data service via HTTP for task registry |

One PostgreSQL instance but the data service is the sole owner — no other service has a DB connection. This is the logical separation of microservices without the operational overhead of managing four databases. In production at scale, each service would own its database independently.

# 3. Service Architecture

## Service map

Client (internal team / demo UI / Mac browser on interview day)

↓

GraphQL Gateway         :8000   ← single entry point for all clients

↓ internal async HTTP (httpx)

Inference Service       :8001   ← DistilBERT + MiniLM NLI

Retrieval Service       :8002   ← MiniLM bi-encoder + FAISS

Data Service            :8003   ← PostgreSQL owner

↓

PostgreSQL              :5432   ← corpus, logs, task registry

Redis                   :6379   ← inference cache, embeddings, rate limiting

## Service responsibilities

| Service | Port | Owns | Does not touch |
| --- | --- | --- | --- |
| GraphQL Gateway | 8000 | GraphQL schema, routing, auth, rate limiting | No ML, no DB direct access |
| Inference Service | 8001 | Model loading, inference logic, Redis cache | No DB, no FAISS |
| Retrieval Service | 8002 | FAISS index, embedding generation | No classification models |
| Data Service | 8003 | PostgreSQL, corpus CRUD, query logging | No models |

## Layered architecture per service (strict call chain)

router → orchestrator (optional) → service → crud → model → PostgreSQL

| Layer | Responsibility | Can call |
| --- | --- | --- |
| Router | HTTP concerns, request validation, error → HTTP status mapping | Service only |
| Orchestrator | Multi-service coordination, avoids circular refs | Service only |
| Service | Business logic | CRUD only |
| CRUD | Raw DB operations — private to each service | Model only |
| Model | ORM definitions | PostgreSQL |

## Adding a new task — the plug-in story

Create new_service/ — new FastAPI service on next available port

Add one GraphQL mutation/query to gateway schema

Add one client method in gateway/clients/

Insert one row into task_registry table

Register in docker-compose.yml

Zero changes to inference, retrieval, or data services.

# 4. Key Architectural Patterns

## 4.1 Repository Pattern (BaseCRUD in shared/)

All DB operations follow a strict hierarchy. The shared package contains a generic BaseCRUD class. Each service's CRUD layer inherits from it and adds only service-specific queries.

BaseCRUD lives in shared because the pattern is universal — any SQLAlchemy + Pydantic project inherits production-grade data access in one line. Fixing a bug or optimising bulk operations once propagates everywhere, across services and across projects.

BaseCRUD provides: get, get_all (with count), create, bulk_create, update, bulk_update, delete.

Future: shared/ becomes a standalone PyPI package. New services do: uv add retail-intelligence-shared

## 4.2 Shared Pydantic schemas

Schemas used by two or more services live in shared/schemas/. Schemas used by only one service live inside that service.

| Location | What lives here | Rule |
| --- | --- | --- |
| shared/schemas/ | ProductResponse, FAQResponse, TaskResponse, QueryLogCreate, ErrorResponse | Used by 2+ services |
| data_service/schemas/ | SeedRequest, SeedResponse, BulkCreateResponse | Data service only |
| inference_service/schemas/ | InferenceRequest, SentimentResponse, IntentResponse, TriageResponse | Inference service only |
| retrieval_service/schemas/ | SearchRequest, SearchResponse, FAQRAGResponse | Retrieval service only |

## 4.3 Async fire-and-forget logging

Query logging never blocks the inference response. After returning the result to the client, the gateway fires a background task to log to the data service.

response = await inference_service.run(request)

asyncio.create_task(log_query(operation, result))  # non-blocking

return response  # returned immediately

Latency impact: zero. The user gets their result, logging happens in background.

## 4.4 Retrieval service corpus loading

The retrieval service loads products and FAQs directly from the data service via HTTP at startup — once. Not per request. The FAISS index is built in memory at startup and reused for all queries.

@asynccontextmanager

async def lifespan(app):

await index_builder.build_from_db()  # once at startup

yield

## 4.5 Redis — three distinct jobs

| Job | Key pattern | TTL | Why |
| --- | --- | --- | --- |
| Inference result cache | inference:{operation}:{sha256(text)} | 1 hour | Identical text submitted twice — don't run inference twice |
| Embedding cache | embedding:{sha256(text)} | 24 hours | Embeddings are deterministic — never recompute |
| Rate limiting | ratelimit:{api_key}:{minute_bucket} | 1 minute | Token bucket per client key |

## 4.6 ENUMs in DB mapped to GraphQL types

Database ENUMs (OperationType, ServedFrom, TaskOperationType) map directly to GraphQL enum types in the gateway schema. This gives type safety from DB through API surface.

## 4.7 Environment configuration (.env / .env.docker)

| File | Used when | Hostname values |
| --- | --- | --- |
| .env | Running locally (uv run uvicorn...) | POSTGRES_HOST=localhost, REDIS_HOST=localhost |
| .env.docker | Running inside Docker containers | POSTGRES_HOST=postgres, REDIS_HOST=redis |

## 4.8 Session context (Redis + pgvector)

Session context is split across two stores. Redis holds lightweight hot state. pgvector holds semantic query embeddings for contextual follow-up queries.

| Store | What it holds | TTL |
| --- | --- | --- |
| Redis | session_id, last_intent, query_count | 30 minutes |
| pgvector (session_queries table) | 384-dim query embeddings per session | Daily cleanup job |

See ADR 001 for full design. Not yet implemented.

# 5. Retail Domain Endpoints

## Design principle

Every endpoint maps to a real question someone on a retail or dunnhumby team asks daily. The API is designed around jobs to be done, not model capabilities.

| Who uses it | Question they have | Endpoint | Model |
| --- | --- | --- | --- |
| Category manager | What department/category does this product belong to? | POST /v1/retail/product-tag | BART zero-shot |
| Retail client team | What is the customer feeling about this product? | POST /v1/retail/review-sentiment | DistilBERT |
| Search/personalisation team | What is this customer actually looking for? | POST /v1/retail/search-intent | MiniLM NLI |
| Customer support team | What kind of complaint is this and how urgent? | POST /v1/retail/complaint-triage | MiniLM NLI |
| Offer/media team | Which products from our catalogue match this query? | POST /v1/retail/product-search | MiniLM + FAISS |
| Insight analyst | A customer asked this — what's the best FAQ answer? | POST /v1/retail/customer-faq | MiniLM + FAISS RAG |

## Platform endpoints

| Endpoint | What it does |
| --- | --- |
| GET /v1/tasks | Discovery — lists all tasks, models, operation types. Powered by task_registry table. |
| GET /health | Liveness check — returns status of all downstream services |
| GET /docs | Swagger UI (data/inference/retrieval services) — auto-generated by FastAPI |
| POST /graphql | GraphQL playground — gateway only, external-facing |

# 6. GraphQL Schema

## Queries vs Mutations — the rule

| Operation type | Used for | Examples |
| --- | --- | --- |
| Query | Reads — safe, idempotent, heavily cached | searchProducts, queryFAQ, availableTasks, health |
| Mutation | Inference — compute, logged, resource-consuming | analyzeSentiment, classifyIntent, triageComplaint |
| Subscription (future) | Real-time streams | Live inference results, monitoring dashboards |

## Schema summary

type Query {

searchProducts(query: String!, topK: Int = 5): [ProductResult!]!

queryFAQ(question: String!): FAQResult!

availableTasks: [TaskInfo!]!

health: HealthStatus!

}

type Mutation {

analyzeSentiment(text: String!): SentimentResult!

classifyIntent(text: String!): IntentResult!

triageComplaint(text: String!): TriageResult!

}

# 7. PostgreSQL Schema

## Tables

| Table | Purpose | Key columns |
| --- | --- | --- |
| products | Product catalogue from dunnhumby dataset | product_id, commodity_desc, department (indexed) |
| faqs | Customer FAQ corpus from Bitext dataset | question, answer, intent_label (indexed) |
| query_logs | All inference/retrieval request logs | operation (ENUM, indexed), input_hash, created_at (indexed) |
| task_registry | Catalogue of available tasks — powers /v1/tasks discovery | name, model, service_url, operation_type (ENUM), is_active |

## GDPR note on query_logs

Raw input text is NEVER stored. Only SHA256 hash of input (for cache lookups) and top result label. We can detect drift and measure latency without reconstructing customer text.

## Database ENUMs

| ENUM | Values | Used in |
| --- | --- | --- |
| OperationType | SENTIMENT, INTENT, TRIAGE, SEARCH, FAQ | query_logs.operation |
| ServedFrom | MODEL, CACHE | query_logs.served_from |
| TaskOperationType | QUERY, MUTATION | task_registry.operation_type |

## Indexes

| Index | Table | Column | Why |
| --- | --- | --- | --- |
| ix_products_department | products | department | get_by_department queries |
| ix_faqs_intent_label | faqs | intent_label | get_by_intent queries |
| ix_query_logs_operation | query_logs | operation | analytics queries by task type |
| ix_query_logs_created_at | query_logs | created_at | time-range analytics |
| ix_query_logs_input_hash | query_logs | input_hash | cache lookup queries |

# 8. Technology Stack

| Layer | Choice | Why |
| --- | --- | --- |
| API entry point | GraphQL via Strawberry + FastAPI | Flexible queries, self-documenting, single endpoint |
| Internal services | FastAPI (REST) | Lightweight, async, easy inter-service HTTP |
| Inter-service calls | httpx (async) | Non-blocking, works natively with FastAPI async |
| ML inference | HuggingFace transformers | Industry standard, pretrained models ready to use |
| Embeddings | sentence-transformers | Best-in-class MiniLM for semantic similarity |
| Vector search | FAISS (swap to Pinecone at scale) | No infra for demo, identical interface to production |
| Cache + rate limiting | Redis | Inference cache, embedding cache, rate limiting — three jobs |
| Database | PostgreSQL 16 | Corpus storage, query logs, task registry |
| ORM + migrations | SQLAlchemy + Alembic | Type-safe queries, managed migrations |
| Settings | pydantic-settings | Env vars with type validation, shared across services |
| Package manager | uv | Fast, reproducible, existing toolchain |
| Containerisation | Docker + docker-compose | One command startup: docker compose up |
| Deployment | Railway | Free tier, postgres/redis addons, public URL, GitHub auto-deploy |
| Code quality | ruff + mypy + pre-commit | Consistent style, type safety, automated checks |

# 9. Transformer vs Classical — Honest Assessment

## The meta-answer (lead with this in the interview)

I want to be direct — transformers are not always the right answer. For sentiment with clean labelled data, classical models are competitive and cheaper. I chose transformers for three specific reasons: operational flexibility (zero-shot avoids retraining cycles), semantic understanding (critical for search and RAG), and a single unified serving infrastructure rather than five different model types to maintain.

| Endpoint | Classical viable? | Transformer advantage | Verdict |
| --- | --- | --- | --- |
| review-sentiment | Yes (85-90% accuracy) | Negation, mixed sentiment, no labelled data needed | Marginal |
| product-tag | No (retraining cost at scale) | Zero-shot, no retraining when categories change | Clear win |
| search-intent | Yes (fixed taxonomy + data) | Variable phrasing, new intents without retraining | Conditional |
| complaint-triage | Yes (labelled historical data) | Subtlety, multilingual without separate models | Mixed |
| product-search | No (keyword fails on semantics) | Semantic understanding, cold-start users | Clear win |
| customer-faq | No (brittle on paraphrases) | Paraphrase matching, novel phrasings | Clear win |

# 10. The Three Models Explained

## Model 1 — DistilBERT (sentiment)

distilbert-base-uncased-finetuned-sst-2-english

Architecture: Encoder-only transformer (BERT family), distilled to 40% smaller

Training: Pre-trained on English text, fine-tuned on SST-2 (67k labelled movie reviews)

What it does: Reads entire input bidirectionally, classifies as POSITIVE or NEGATIVE

Why it's fast: 6 layers instead of BERT's 12, 40% fewer parameters, same accuracy on most tasks

Confidence: 0.99+ on clear sentiment

## Model 2 — MiniLM cross-encoder (intent + triage)

cross-encoder/nli-MiniLM2-L6-H768

Architecture: Cross-encoder — takes two inputs (text + candidate label) and scores how well they match

Training: Trained on Natural Language Inference — given premise and hypothesis, predict entailment/contradiction/neutral

What it does: For each candidate label, asks 'does this text entail the label [return]?' — scores all labels, returns ranked list

Why confidence is lower: Repurposing NLI reasoning for classification — never trained on your specific labels

Why it's the right choice: Adding a new intent category requires only a new label string, no retraining

## Model 3 — MiniLM bi-encoder (retrieval + RAG)

all-MiniLM-L6-v2

Architecture: Bi-encoder — encodes query and corpus separately into 384-dimensional vectors

Training: Contrastive learning on millions of sentence pairs — similar sentences get similar vectors

What it does: Encodes query to a vector, finds nearest neighbours in FAISS index

Why this is powerful: 'healthy breakfast' matches 'low-fat yoghurt' — no shared keywords needed

# 11. Data Sources

## dunnhumby 'The Complete Journey' — Product corpus

Source: https://www.kaggle.com/datasets/frtgnn/dunnhumby-the-complete-journey

I used dunnhumby's own public dataset as the product corpus. It felt appropriate and gave the demo genuine domain relevance — these are real SKU categories from a real retailer.

| Column | Used for |
| --- | --- |
| COMMODITY_DESC | RAG product search corpus (primary text) |
| SUB_COMMODITY_DESC | Zero-shot category tags |
| DEPARTMENT | Intent classification labels |

## Bitext Customer Support Dataset — FAQ corpus

Source: https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset

| Column | Used for |
| --- | --- |
| instruction | Intent classifier input examples |
| intent | Classification labels (27 classes) |
| response | RAG FAQ answer corpus |

# 12. Key Production Considerations

## 12.1 Latency

Problem: Transformer inference is slow on CPU (200-800ms per request)

What we do: Load models once at startup, never per request. Use DistilBERT (40% faster than BERT-base)

Production levers: INT8 quantisation (2-4x speedup), ONNX export, GPU deployment, async batching

Numbers to cite: DistilBERT CPU ~50ms, GPU ~5ms. MiniLM embeddings ~20ms CPU

## 12.2 Model loading strategy

Problem: Loading a transformer takes 2-10 seconds

What we do: Load all models into memory at startup via model_loader.py singleton

Production: Warm pool of model instances behind a load balancer. Health check confirms loaded before routing traffic

## 12.3 Scalability

Horizontal first: Multiple pods behind a load balancer. Models are stateless so this is trivial

Vertical next: GPU instance (T4 or A10G) for 10-20x latency improvement

Batching: Aggregate concurrent requests into a single forward pass — critical at high QPS

Connection pooling: SQLAlchemy pool_size=10, max_overflow=20. PgBouncer for production scale (see ADR 002)

## 12.4 Model versioning

Problem: You update a model — do all consumers break?

Pattern: Version in the URL (/v1/, /v2/). Run old + new simultaneously during rollout (blue/green)

In production: MLflow or HuggingFace model registry for lineage and rollback

## 12.5 Monitoring and observability

What to track: Request latency (p50/p95/p99), error rate, prediction distribution drift, model confidence scores

Tools: Prometheus + Grafana for metrics, structlog for request logs, Evidently for drift

Alert on: p99 latency > 500ms, error rate > 1%, sentiment distribution shift > 10% week-on-week

## 12.6 GDPR / data privacy

Customer text is PII — may contain names, locations, purchase intent

What we do: No raw text in query_logs — only SHA256 hash. Input text never stored.

Production: Data stays in-region (EU deployment for dunnhumby). No third-party model APIs — inference on-premises

## 12.7 Cold start

Problem: First request after deployment is slow (model loading + JIT compilation)

Solution: Health check endpoint warms the model. Load balancer only routes traffic once /health returns 200

Production: Keep minimum 1 pod always warm — no scale-to-zero for latency-sensitive models

## 12.8 Auth and security

Minimum: API key in Authorization: Bearer <key> header

Production: OAuth2 with scopes, rate limiting per client (Redis token bucket), WAF in front

# 13. Architecture Decision Records (ADR Index)

All ADRs live in docs/adr/ in the repository. Summary below.

| ADR | Title | Status | When to implement |
| --- | --- | --- | --- |
| 001 | Session Context Management | Proposed | When gateway service is built |
| 002 | PgBouncer Connection Pooling | Proposed | Day 3 production hardening |
| 003 | pgvector for Embedding Storage | Proposed | After FAISS working end to end |
| 004 | User Management | Proposed | After core services working |
| 005 | Performance Optimisations | Partially applied | Ongoing — deferred items in ADR |
| 006 | Testing Strategy | Planned | Day 3 |
| 007 | Model Evaluation and Cost Matrix | Planned | Day 5 |

## ADR 001 — Session Context (summary)

Redis: session_id + last_intent + query_count (TTL 30 minutes)

pgvector: 384-dim query embeddings per session (daily cleanup)

Semantic context retrieval: follow-up queries understood by similarity, not keyword matching

## ADR 005 — Performance Optimisations (applied items)

Indexes added: ix_products_department, ix_faqs_intent_label, ix_query_logs_operation, ix_query_logs_created_at, ix_query_logs_input_hash

Combined count + fetch: single query with COUNT(*) OVER() window function

Bounded fetches: all get_by_* methods now accept skip and limit parameters

# 14. Day-by-Day Schedule

## BUILD PHASE (Days 1-4)

| Day | Focus | Done when |
| --- | --- | --- |
| Day 0 (today) | Project scaffold, docker-compose, postgres + redis, data service complete, inference service complete | All 3 endpoints return real predictions. Redis caching working. |
| Day 1 | Retrieval service — MiniLM + FAISS, semantic product search, FAQ RAG | searchProducts and queryFAQ return real results from dunnhumby corpus |
| Day 2 | Gateway — GraphQL, Strawberry, all mutations and queries wired, Redis auth | Full GraphQL playground working. All 5 tasks callable from single endpoint. |
| Day 3 | Docker — Dockerfiles for all services, docker-compose wires all 5, deploy to Railway, tests | docker compose up brings everything up. Live Railway URL accessible from Mac. |
| Day 4 | Polish — seed data loaded, README, demo flow rehearsed end to end | Complete demo runs in 5 minutes with live URL on Railway |

## PREPARE PHASE (Days 5-8)

| Day | Focus | Output |
| --- | --- | --- |
| Day 5 | Architecture diagrams + model evaluations + cost matrix | Architecture diagram. Cost matrix comparing 2-3 models per task. |
| Day 6 | Build presentation + first rehearsal | 5-minute talk structured and rehearsed once |
| Day 7 | Stress test — timed rehearsals + hard questions | Confident answers to all 10 hard questions |
| Day 8 | Final prep + rest | One final rehearsal. Confirm Railway URL live. |

# 15. Hard Questions to Prep

| # | Question | Key points in answer |
| --- | --- | --- |
| 1 | Why not just use one model for all tasks? | Different architectures for different problems. DistilBERT for classification, MiniLM for similarity, cross-encoder for zero-shot. |
| 2 | Why REST internally and GraphQL at gateway? | Internal calls have fixed known shapes — GraphQL overhead adds complexity with no benefit. External clients need flexibility. |
| 3 | How would this handle 10,000 requests per second? | Horizontal scaling (stateless services), GPU deployment (10-20x latency), async batching, Redis cache hit rate, PgBouncer. |
| 4 | What happens when a new task needs to be added? | New service + new GraphQL mutation + new task_registry row. Zero changes to existing services. |
| 5 | How do you prevent model drift in production? | query_logs table. Track label distribution week-on-week. Alert on >10% shift. Evidently for automated drift detection. |
| 6 | What's your GDPR strategy? | No raw text stored. SHA256 hash only. On-premises inference. EU deployment. No third-party APIs. |
| 7 | Why FAISS and not a proper vector database? | Same conceptual pattern as Pinecone/Weaviate. One file change to swap. Demo scale doesn't need the infra overhead. |
| 8 | How would you A/B test two model versions? | Blue/green deployment. Route 10% traffic to new model. Compare label distributions and latency in query_logs. Shadow mode. |
| 9 | What's the cost at dunnhumby scale? | DistilBERT at 50ms CPU = 72k req/hr on c5.xlarge ($0.17/hr) = ~$2.36 per 1M requests. GPU reduces by 10x. |
| 10 | If you had 3 more months, what would you build next? | Fine-tuning on dunnhumby labelled data. pgvector for embeddings. Async batching. Full monitoring with Evidently drift detection. |

# 16. Demo Flow (5 minutes)

| Time | What you say / do |
| --- | --- |
| 0:00 - 0:30 | Problem framing: 'Here is how I scoped the brief. The question is underspecified by design — I treated that as an invitation to make explicit architectural decisions and justify them.' |
| 0:30 - 2:00 | Architecture walkthrough: 'Four services, one GraphQL surface, a retrieval layer for grounding in business data.' Show architecture diagram. |
| 2:00 - 3:30 | Live demo: Hit /graphql — analyzeSentiment on a product review. Show cached: false then cached: true. searchProducts with 'healthy breakfast options'. queryFAQ with a customer question. |
| 3:30 - 4:30 | Key considerations: 'The three things that matter most in production: latency, GDPR, and model drift detection.' |
| 4:30 - 5:00 | What's next: 'With more time: fine-tuning on dunnhumby labelled data, async batching, pgvector for persistent embeddings, shadow deployments for safe model updates.' |
| 5:00 | STOP. Hard stop. Do not keep talking. |

# 17. Glossary

| Term | What it means |
| --- | --- |
| Transformer | Neural network architecture using attention mechanisms. BERT, GPT, T5 are all transformers. |
| Pipeline | HuggingFace abstraction: pipeline('sentiment-analysis') gives you a working model in 2 lines. |
| Tokenisation | Converting text to numbers the model can process. Transformers can't read words directly. |
| Pretrained model | A model already trained on massive data. You use it as-is or fine-tune it. |
| Fine-tuning | Taking a pretrained model and training it further on your specific data. |
| Encoder | Transformer that reads the whole sequence (BERT). Good for classification. |
| Cross-encoder | Takes two inputs together, scores how well they match. Used for zero-shot NLI. |
| Bi-encoder | Two encoders producing embeddings you can compare. Used in semantic search. |
| Embedding | A fixed-size vector representing text meaning. Similar texts have similar vectors. |
| FAISS | Facebook's library for fast nearest-neighbour search over embeddings. |
| RAG | Retrieval-Augmented Generation: retrieve relevant docs, use them to ground a response. |
| Zero-shot | Classifying into categories the model has never seen during training. |
| Quantisation | Compressing model weights (float32 to int8) for faster inference at slight accuracy cost. |
| Pydantic | Python library for data validation. Defines what requests/responses must look like. |
| p99 latency | The latency that 99% of requests fall under. The real production metric. |
| BaseCRUD | Generic CRUD class in shared/. Inherited by all service-specific CRUD classes. |
| Repository pattern | All DB queries in one place per model. Routers never contain SQL. |
| ENUMs | Fixed set of values enforced by the database. Maps to GraphQL enum types. |
| pgvector | PostgreSQL extension for storing and querying vector embeddings natively. |
