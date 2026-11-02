from dataclasses import dataclass, field
from collections.abc import Hashable
from uuid import UUID, uuid4

from .colour import Colour


@dataclass(slots=True, eq=False)
class Edge:
    id:Hashable
    uid:UUID = field(
        default_factory=uuid4,
        init=False,
        repr=False
    )

    source:Hashable
    target:Hashable

    label:str = ""
    colour:Colour = field(default_factory=Colour)

    attributes:dict = field(default_factory=dict)
    origin_key:Hashable|None = None


def edge_identity(edge:Edge, directed:bool):
    if edge.id is not None:
        return "id", edge.id
    
    endpoints = (
        (edge.source, edge.target)
        if directed
        else frozenset((edge.source, edge.target))
    )

    return "endpoints", endpoints
