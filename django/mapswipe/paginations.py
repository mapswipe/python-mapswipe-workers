from __future__ import annotations
from typing import List, TypeVar, Generic, Any
import strawberry

from strawberry_django import utils
from strawberry_django.fields.field import StrawberryDjangoField

from strawberry.arguments import UNSET
from strawberry_django.pagination import StrawberryDjangoPagination
from strawberry_django.pagination import apply as apply_pagination

from django.db.models import QuerySet


class CountBeforePaginationMonkeyPatch(StrawberryDjangoPagination):
    def get_queryset(self, queryset: QuerySet[Any], info, pagination=UNSET, **kwargs):
        self.count = queryset.count()
        queryset = apply_pagination(pagination, queryset)
        return super(StrawberryDjangoPagination, self)\
            .get_queryset(queryset, info, **kwargs)


StrawberryDjangoPagination.get_queryset = CountBeforePaginationMonkeyPatch.get_queryset

E = TypeVar("E")


@strawberry.type
class CountList(Generic[E]):
    count: int
    items: List[E]


class StrawberryDjangoCountList(StrawberryDjangoField):
    @property
    def is_list(self):
        return True

    @property
    def django_model(self):
        # Hack to get the nested type of `CountList` to register
        # as the type of this field
        items_type = [
            f.type
            for f in self.type._type_definition._fields
            if f.name == 'items'
        ]
        if len(items_type) > 0:
            type_ = utils.unwrap_type(items_type[0])
            self._base_type = type_
            return utils.get_django_model(type_)
        return None

    def resolver(self, info, source, **kwargs):
        qs = super().resolver(info, source, **kwargs)
        return CountList[self._base_type](
            count=self.count,
            # items=qs,
            items=list(qs),  # FIXME:
        )