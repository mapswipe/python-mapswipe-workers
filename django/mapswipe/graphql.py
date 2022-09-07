from typing import Any, Optional, Union

import strawberry
from apps.existing_database.query import Query as ExistingDatabaseQuery
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from strawberry.django.views import AsyncGraphQLView

from .dataloaders import GobalDataLoader

# from strawberry_django_plus.optimizer import DjangoOptimizerExtension


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(
        self,
        request: Union[Request, WebSocket],
        response: Optional[Response],
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


schema = strawberry.Schema(
    query=Query,
    mutation=None,
    extensions=[
        # DjangoOptimizerExtension,
    ],
)
