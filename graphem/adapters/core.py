from abc import ABC, abstractmethod


class Adapter(ABC):

    def __init__(self):
        ...

    @classmethod
    @abstractmethod
    def build_graph(cls, *args, **kwargs):
        ...

    @staticmethod
    @abstractmethod
    def get_edge_attribute(values, key):
        ...

    @staticmethod
    @abstractmethod
    def get_node_attribute(values, key):
        ...