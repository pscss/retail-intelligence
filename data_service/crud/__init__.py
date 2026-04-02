"""Data service CRUD operations."""

from data_service.crud.faq import FAQCrud, faq_crud
from data_service.crud.product import ProductCRUD, product_crud
from data_service.crud.query_log import QueryLogCRUD, query_log_crud
from data_service.crud.task import TaskCRUD, task_crud

__all__ = [
    "FAQCrud",
    "faq_crud",
    "ProductCRUD",
    "product_crud",
    "QueryLogCRUD",
    "query_log_crud",
    "TaskCRUD",
    "task_crud",
]
