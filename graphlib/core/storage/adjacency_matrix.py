import numpy as np
from typing import Iterable, Any, Tuple

from base import GraphStorage


class AdjacencyMatrix(GraphStorage):
    def __init__(self):
        self._body = np.zeros()

    def add_node(self, v):
        ...

    def add_edge(self, u, v, weight=1):
        ...

    def neighbours(self, v):
        ...

    def nodes(self) -> Iterable[Any]:
        ...

    def edges(self) -> Iterable[Tuple[Any, Any, float]]:
        ...
