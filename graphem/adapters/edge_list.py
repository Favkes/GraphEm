from collections.abc import Hashable, Iterable

from ..core.graph import Graph
from ..core.editor import GraphEditor
# from ..core.colour import Colour
# from ..core.position import Position
from ..core.node import Node
from ..core.edge import Edge


def from_edge_list(
        edges:Iterable[tuple[Hashable,Hashable]],
        *,
        directed:bool = False) -> Graph:
    graph = Graph(
        directed=directed,
        allow_parallel_edges=True
    )
    editor = GraphEditor(graph)

    for source, target in edges:

        for node_id in (source, target):
            if node_id not in graph.nodes:
                editor.add_node(
                    Node(id=node_id, label=str(node_id))
                )

        editor.add_edge(
            Edge(
                id=(source, target),
                source=source,
                target=target
            )
        )

    return graph
