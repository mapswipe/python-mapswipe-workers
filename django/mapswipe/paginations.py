from __future__ import annotations

import copy
from typing import Any, Callable, Generic, Type, TypeVar

import strawberry
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import QuerySet
from strawberry_django import utils
from strawberry_django.fields.field import StrawberryDjangoField
from strawberry_django.pagination import (
    OffsetPaginationInput,
    StrawberryDjangoPagination,
)
from strawberry_django.resolvers import django_resolver


def process_pagination(pagination):
    """
    Mutate pagination object to make sure limit are under given threshold
    """
    if pagination is strawberry.UNSET or pagination is None:
        pagination = OffsetPaginationInput(
            offset=0,
            limit=settings.DEFAULT_PAGINATION_LIMIT,
        )
    if pagination.limit == -1:
        pagination.limit = settings.DEFAULT_PAGINATION_LIMIT
    pagination.limit = min(pagination.limit, settings.MAX_PAGINATION_LIMIT)
    return pagination


def apply_pagination(pagination, queryset):
    pagination = process_pagination(pagination)
    start = pagination.offset
    stop = start + pagination.limit
    return queryset[start:stop]


class CountBeforePaginationMonkeyPatch(StrawberryDjangoPagination):
    def get_queryset(
        self,
        queryset: QuerySet[Any],
        info,
        pagination=strawberry.UNSET,
        **kwargs,
    ) -> QuerySet:
        queryset = super(StrawberryDjangoPagination, self).get_queryset(
            queryset, info, **kwargs
        )
        queryset = apply_pagination(pagination, queryset)
        return queryset


StrawberryDjangoPagination.get_queryset = CountBeforePaginationMonkeyPatch.get_queryset
OffsetPaginationInput.limit = 1  # TODO: This is not working

DjangoModelTypeVar = TypeVar("DjangoModelTypeVar")


@strawberry.type
class CountList(Generic[DjangoModelTypeVar]):
    limit: int
    offset: int
    queryset: strawberry.Private[QuerySet | list[DjangoModelTypeVar]]
    get_count: strawberry.Private[Callable]

    @strawberry.field
    async def count(self) -> int:
        return await self.get_count()

    @strawberry.field
    async def items(self) -> list[DjangoModelTypeVar]:
        queryset = self.queryset
        if type(self.queryset) in [list, tuple]:
            return queryset
        return [d async for d in queryset]


class StrawberryDjangoCountList(StrawberryDjangoField):
    @property
    def is_list(self):
        return True

    @property
    def django_model(self):
        # Hack to get the nested type of `CountList` to register
        # as the type of this field
        items_type = [
            f.type for f in self.type._type_definition._fields if f.name == "items"
        ]
        if len(items_type) > 0:
            type_ = utils.unwrap_type(items_type[0])
            self._base_type = type_
            return utils.get_django_model(type_)
        return None

    def resolver(
        self,
        info,
        source,
        pk=strawberry.UNSET,
        filters: Type = strawberry.UNSET,
        order: Type = strawberry.UNSET,
        pagination: Type = strawberry.UNSET,
    ):
        if self.django_model is None or self._base_type is None:
            # This needs to be fixed by developers
            raise Exception("django_model should be defined!!")

        queryset = self.django_model.objects.all()

        type_ = self._base_type or self.child.type
        type_ = utils.unwrap_type(type_)
        get_queryset = getattr(type_, "get_queryset", None)
        if get_queryset:
            queryset = get_queryset(type_, queryset, info)

        queryset = self.apply_filters(queryset, filters, pk, info)
        queryset = self.apply_order(queryset, order)

        _current_queryset = copy.copy(queryset)

        @sync_to_async
        def get_count():
            return _current_queryset.count()

        pagination = process_pagination(pagination)

        queryset = self.apply_pagination(queryset, pagination)
        return CountList[self._base_type](
            get_count=get_count,
            queryset=queryset,
            limit=pagination.limit,
            offset=pagination.offset,
        )


def pagination_field(
    resolver=None,
    *,
    name=None,
    field_name=None,
    filters=strawberry.UNSET,
    default=strawberry.UNSET,
    **kwargs,
) -> Any:
    field_ = StrawberryDjangoCountList(
        python_name=None,
        graphql_name=name,
        type_annotation=None,
        filters=filters,
        django_name=field_name,
        default=default,
        **kwargs,
    )
    if resolver:
        resolver = django_resolver(resolver)
        return field_(resolver)
    return field_
