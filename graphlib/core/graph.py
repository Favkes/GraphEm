import numpy as np
from .base import GraphBase


class Graph(GraphBase):

    def __init__(self):
        self.nodes = []
        self.edges = []

    def __repr__(self):
        return f"<Graph nodes={str(self.nodes)} edges={str(self.edges)}>"


if __name__=="__main__":
    g = Graph()
    print(g)
