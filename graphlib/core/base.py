from abc import ABC, abstractmethod


class GraphBase(ABC):
    @abstractmethod
    def add_node(self, v): ...

    @abstractmethod
    def add_edge(self, u, v, weight=1): ...

    @abstractmethod
    def neighbours(self, v): ...

