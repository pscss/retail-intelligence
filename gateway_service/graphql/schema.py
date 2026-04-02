"""GraphQL schema composition."""

import strawberry

from gateway_service.graphql.mutations import Mutation
from gateway_service.graphql.queries import Query

graphql_schema = strawberry.Schema(query=Query, mutation=Mutation)
