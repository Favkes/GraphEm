from dataclasses import dataclass, field
from collections.abc import Hashable
from .colour import Colour
from .position import Position


@dataclass(slots=True)
class Node:
    id: Hashable

    pos:Position = field(default_factory=Position)

    colour:Colour = field(default_factory=Colour)
    radius:float = 10
    label:str = ""

    attributes:dict = field(default_factory=dict)

