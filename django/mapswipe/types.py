import json
from typing import NewType
import strawberry
from strawberry.scalars import JSON


# TODO:
EnumDisplay = strawberry.scalar(
    NewType("EnumDisplay", str),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


TimeInSeconds = strawberry.scalar(
    NewType("TimeInSeconds", int),
    serialize=lambda v: round(v),
    parse_value=lambda v: v,
)

AreaSqKm = strawberry.scalar(
    NewType("AreaSqKm", float),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

GenericJSON = strawberry.scalar(
    NewType("GenericJSON", JSON),
    serialize=lambda v: json.loads(v) if type(v) == str else v,
    parse_value=lambda v: v,
)
