"""Data service routers."""

from data_service.routers.faqs import router as faqs_router
from data_service.routers.products import router as products_router
from data_service.routers.query_logs import router as query_logs_router
from data_service.routers.tasks import router as tasks_router

__all__ = [
    "faqs_router",
    "products_router",
    "query_logs_router",
    "tasks_router",
]
