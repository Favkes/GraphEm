from collections.abc import Hashable
from uuid import UUID
from .edge import Edge
from .node import Node
from .graph import Graph


class GraphEditor:
    graph:Graph

    def __init__(self, graph:Graph):
        self.graph = graph

    def add_node(self, node:Node):
        if node.id in self.graph.nodes:
            raise ValueError(f"Duplicate node: {node.id}")
        self.graph.nodes[node.id] = node

    def add_edge(self, edge:Edge) -> None:
        if edge.source not in self.graph.nodes:
            raise ValueError(f"Unknown node: {edge.source}")

        if edge.target not in self.graph.nodes:
            raise ValueError(f"Unknown node: {edge.target}")

        key = (
            (edge.source, edge.target)
            if self.graph.directed
            else frozenset((edge.source, edge.target))
        )

        if not self.graph.allow_parallel_edges:
            if self.graph.edges.get(key):
                raise ValueError(f"Duplicate edge: {key}")

        self.graph.edges.setdefault(key, {})[edge.uid] = edge

    def remove_node(self, node_id:Hashable) -> None:
        if node_id not in self.graph.nodes:
            raise ValueError(f"Nonexistent node: {node_id}")
        del self.graph.nodes[node_id]

    def remove_edge(self, edge:Edge, target_exact:bool = False) -> None:
        key = self._edge_key(edge)
        edge_group:dict[UUID,Edge] = self.graph.edges.get(key)

        if not edge_group:
            raise ValueError(f"Nonexistent edge group: {key}")

        if edge.uid in edge_group and edge_group[edge.uid] == edge:
            matching_uid = edge.uid
        else:
            matching_uid = next(
                (uid for uid, existing in edge_group.items() if existing == edge),
                None
            )
        if matching_uid is None:
            if target_exact:
                raise ValueError(f"No exact matching edge: {edge}") from None
            # fallback -> remove first edge
            matching_uid = next(iter(edge_group))

        del edge_group[matching_uid]

        # clean up leftover empty groups
        if not edge_group:
            del self.graph.edges[key]

    def remove_edges_of_id(self, edge_id:Hashable) -> None:
        if edge_id not in self.graph.edges:
            raise ValueError(f"Nonexistent edge: {edge_id}")
        del self.graph.edges[edge_id]

    def _edge_key(self, edge:Edge) -> Hashable:
        return (
            (edge.source, edge.target)
            if self.graph.directed
            else frozenset((edge.source, edge.target))
        )

