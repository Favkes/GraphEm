from collections.abc import Hashable, Iterable, Sequence
import random

from ..adapters.core import Adapter
from ..core.graph import Graph
from ..core.editor import GraphEditor
from ..core.node import Node
from ..core.edge import Edge


class EdgeListAdapter(Adapter):
    def __init__(self, edges):
        super().__init__()
        self.edges = edges

    def build_graph(
            self,
            *,
            directed:bool = False) -> Graph:
        graph = Graph(
            directed=directed,
            allow_parallel_edges=True,
            origin_adapter=self
        )
        editor = GraphEditor(graph)

        for i, (source, target) in enumerate(self.edges):

            for node_id in (source, target):
                if node_id not in graph.nodes:
                    editor.add_node(
                        Node(id=node_id, label=str(node_id))
                    )

            editor.add_edge(
                Edge(
                    id=(source, target),
                    source=source,
                    target=target,
                    origin_key=i
                )
            )

        for node in graph.nodes.values():
            node.pos.val = (random.randint(0, 700), random.randint(0, 700))

        return graph

    @staticmethod
    def get_edge_attribute(values, edge:Edge, default = None):
        return values[edge.origin_key] if edge.origin_key is not None else None

    @staticmethod
    def get_node_attribute(values, node:Node, default = None):
        return values[node.id]
