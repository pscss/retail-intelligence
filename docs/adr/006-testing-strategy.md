# ADR 006 — Testing Strategy

## Status
Planned — implementation Day 3

## Context
Each service needs tests at three levels:
- Unit: test business logic in isolation (mock DB, mock models)
- Integration: test endpoints with real DB (test database)
- E2E: test full request flow through gateway → services

## Structure
```
tests/
├── conftest.py                    ← shared fixtures (test DB, mock models)
├── data_service/
│   ├── test_crud.py               ← unit tests for CRUD operations
│   ├── test_services.py           ← unit tests for service layer
│   └── test_routers.py            ← integration tests for HTTP endpoints
├── inference_service/
│   ├── test_model_loader.py       ← unit tests for model loading
│   ├── test_services.py           ← unit tests with mocked models
│   └── test_routers.py            ← integration tests
├── retrieval_service/
│   ├── test_faiss_index.py        ← unit tests for index build/search
│   └── test_routers.py            ← integration tests
└── gateway/
    ├── test_queries.py            ← GraphQL query tests
    ├── test_mutations.py          ← GraphQL mutation tests
    └── test_auth.py               ← API key auth tests
```

## Tools
- pytest + pytest-asyncio for async tests
- httpx AsyncClient for endpoint testing
- pytest-mock for mocking models and DB
- factory-boy for test data generation
- coverage target: 80% minimum per service

## Test database strategy
- Separate test DB: `retail_intelligence_test`
- Alembic migrations run at test session start
- Each test rolls back in a transaction — no persistent state
- Never use production DB in tests

## CI integration (Day 3 alongside tests)
- GitHub Actions runs tests on every push to develop
- PR to master blocked if tests fail
- Coverage report posted as PR comment

## When to implement
Day 3 — after all services are running end to end.
