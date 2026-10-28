from dataclasses import dataclass, field
from collections.abc import Hashable
from uuid import UUID

from .colour import Colour
from .position import Position
from .node import Node
from .edge import Edge


@dataclass(slots=True)
class Graph:
    nodes:dict[Hashable,Node] = field(default_factory=dict)
    edges:dict[Hashable,dict[UUID,Edge]] = field(default_factory=dict)

    directed:bool = False
    allow_parallel_edges:bool = True
