from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Any


class GraphStorage(ABC):

    @abstractmethod
    def add_node(self, v) -> None:
        """ Adds a new node (vertex). """

    @abstractmethod
    def add_edge(self, u, v, weight=1) -> None:
        """ Adds an edge between u and v with optional weight. """

    @abstractmethod
    def neighbours(self, v) -> Iterable[Tuple[Any, float]]:
        """ Returns tuples of (neighbour, weight) """

    @abstractmethod
    def nodes(self) -> Iterable[Any]:
        """ Iterating over the nodes (vertices). """

    @abstractmethod
    def edges(self) -> Iterable[Tuple[Any, Any, float]]:
        """ Iterating over the edges. """
