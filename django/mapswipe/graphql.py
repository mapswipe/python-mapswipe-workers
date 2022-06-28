import strawberry
from typing import Any, Optional, Union

from strawberry.django.views import AsyncGraphQLView
from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import Response
# from strawberry_django_plus.optimizer import DjangoOptimizerExtension

from apps.existing_database.query import Query as ExistingDatabaseQuery
from .dataloaders import GobalDataLoader


class CustomAsyncGraphQLView(AsyncGraphQLView):

    async def get_context(
        self,
        request: Union[Request, WebSocket],
        response: Optional[Response],
    ) -> Any:
        return {
            'request': request,
            'dl': GobalDataLoader(),
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
    ]
)
