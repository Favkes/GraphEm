from typing import Iterable, Any, Tuple

from base import GraphStorage


class AdjacencyMap(GraphStorage):
    _adj: dict[
        int,
        list[tuple[int, int]]
    ]
    _nodes: dict[int, Any]

    def __init__(self):
        self._adj = {}
        self._nodes = {}

    def add_node(self,
                 v: int,
                 label: Any = None):
        self._adj.setdefault(v, [])

        if label is None:
            label = len(self._adj)
        self._nodes.setdefault(v, label)

    def add_edge(self,
                 u: int,
                 v: int,
                 weight: int = 1):
        self._adj[u].append((v, weight))

    def neighbours(self, v):
        return self._adj.get(v, [])

    def nodes(self) -> Iterable[Any]:
        ...

    def edges(self) -> Iterable[Tuple[Any, Any, float]]:
        ...
