from typing import Any, Union

import sentry_sdk
import strawberry
from apps.existing_database.query import Query as ExistingDatabaseQuery
from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry.django.views import AsyncGraphQLView
from strawberry.types import ExecutionResult

from .dataloaders import GobalDataLoader

# from strawberry_django_plus.optimizer import DjangoOptimizerExtension


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(
        self,
        request: Union[Request, WebSocket],
        **_,
    ) -> Any:
        return {
            "request": request,
            "dl": GobalDataLoader(),
        }


@strawberry.type
class Query(
    ExistingDatabaseQuery,
):
    pass


class Schema(strawberry.Schema):
    def _scope_with_sentry(self, execute_func, *args, **kwargs) -> ExecutionResult:
        operation_name = kwargs.get("operation_name")
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("kind", operation_name)
            scope.transaction.name = operation_name
            return execute_func(*args, **kwargs)

    def execute_sync(self, *args, **kwargs) -> ExecutionResult:
        return self._scope_with_sentry(super().execute_sync, *args, **kwargs)

    def execute(self, *args, **kwargs) -> ExecutionResult:
        return self._scope_with_sentry(super().execute, *args, **kwargs)


schema = Schema(
    query=Query,
    mutation=None,
    extensions=[
        # DjangoOptimizerExtension,
    ],
)
