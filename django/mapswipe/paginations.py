from __future__ import annotations

import copy
from typing import Any, Generic, List, TypeVar

import strawberry
from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from strawberry.arguments import UNSET
from strawberry_django import utils
from strawberry_django.fields.field import StrawberryDjangoField
from strawberry_django.pagination import (
    OffsetPaginationInput,
    StrawberryDjangoPagination,
)
from strawberry_django.pagination import apply as apply_pagination


class CountBeforePaginationMonkeyPatch(StrawberryDjangoPagination):
    def get_queryset(self, queryset: QuerySet[Any], info, pagination=UNSET, **kwargs):
        _current_queryset = copy.copy(queryset)

        @sync_to_async
        def _get_count():
            return _current_queryset.count()

        self.count_callback = _get_count
        queryset = apply_pagination(pagination, queryset)
        return super(StrawberryDjangoPagination, self).get_queryset(
            queryset, info, **kwargs
        )


StrawberryDjangoPagination.get_queryset = CountBeforePaginationMonkeyPatch.get_queryset
OffsetPaginationInput.limit = 1  # TODO: This is not working

DjangoModelTypeVar = TypeVar("DjangoModelTypeVar")


@strawberry.type
class CountList(Generic[DjangoModelTypeVar]):
    @staticmethod
    def resolve_count(root):
        return root.node["count_callback"]()

    @staticmethod
    async def resolve_items(root):
        @sync_to_async
        def _get_list():
            return list(root.node["queryset"])

        items = await _get_list()
        return items

    count: int = strawberry.field(resolver=resolve_count)
    items: List[DjangoModelTypeVar] = strawberry.field(resolver=resolve_items)

    def __init__(self, *args, **kwargs):
        self.node = kwargs.pop("node", {})
        super().__init__(*args, **kwargs)


class StrawberryDjangoCountList(CountList[DjangoModelTypeVar], StrawberryDjangoField):
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

    def resolver(self, info, source, **kwargs):
        qs = super().resolver(info, source, **kwargs)
        return CountList[self._base_type](
            node=dict(
                count_callback=self.count_callback,
                queryset=qs,
            )
        )

    def get_queryset(self, queryset, info, order=UNSET, **kwargs):
        type_ = self._base_type or self.child.type
        type_ = utils.unwrap_type(type_)
        get_queryset = getattr(type_, "get_queryset", None)
        if get_queryset:
            queryset = get_queryset(self, queryset, info, **kwargs)
        return super().get_queryset(queryset, info, order=order, **kwargs)
