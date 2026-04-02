"""Gateway service exposing a unified GraphQL API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from strawberry.fastapi import GraphQLRouter

from gateway_service.clients.data_client import data_client
from gateway_service.clients.inference_client import inference_client
from gateway_service.clients.retrieval_client import retrieval_client
from gateway_service.graphql.schema import graphql_schema
from gateway_service.graphql.types import HealthType
from shared.config import settings
from shared.redis_client import close_redis


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware — mirrors dunnhumby PermissionMiddleware."""

    OPEN_PATHS = {"/health", "/graphql"}

    async def dispatch(self, request: Request, call_next):
        # Allow GET requests (playground UI)
        if request.method == "GET":
            return await call_next(request)

        # Allow introspection queries (schema exploration)
        body = await request.body()
        if b"IntrospectionQuery" in body or b"__schema" in body:
            return await call_next(request)

        # Validate API key
        api_key = request.headers.get("X-Api-Key") or request.headers.get(
            "Authorization", ""
        ).removeprefix("Bearer ")
        if not api_key or api_key != settings.api_key:
            return JSONResponse(
                {"detail": "Invalid or missing API key"},
                status_code=401,
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for gateway service."""
    print(f"Starting {settings.project_name} gateway-service...")
    await inference_client.start()
    await retrieval_client.start()
    await data_client.start()
    yield
    await inference_client.stop()
    await retrieval_client.stop()
    await data_client.stop()
    await close_redis()
    print("Shutting down gateway-service...")


class GatewayApplication:
    """Builds and configures the gateway FastAPI app."""

    def __init__(self) -> None:
        self.app = FastAPI(
            title="Retail Intelligence - Gateway Service",
            description="GraphQL API gateway for inference and retrieval operations.",
            version="0.1.0",
            lifespan=lifespan,
        )
        self.app.add_middleware(APIKeyMiddleware)
        self._mount_graphql()
        self._register_routes()

    def _mount_graphql(self) -> None:
        graphql_app = GraphQLRouter(
            schema=graphql_schema,
            graphql_ide="graphiql",
        )
        self.app.include_router(graphql_app, prefix="/graphql")

    def _register_routes(self) -> None:
        @self.app.get("/health")
        async def health() -> HealthType:
            return HealthType(service="gateway-service", status="healthy")


app = GatewayApplication().app
