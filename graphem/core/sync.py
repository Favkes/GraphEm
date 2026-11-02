from collections.abc import Hashable, Sequence, Mapping

from ..core.graph import Graph
from ..core.editor import GraphEditor
from ..core.edge import Edge
from ..adapters.core import Adapter


class GraphSynchronizer:
    graph:Graph
    editor:GraphEditor
    adapter:Adapter|None

    _edge_bindings:dict[Hashable,Sequence|Mapping]
    _node_bindings:dict[Hashable,Sequence|Mapping]


    def __init__(self, graph:Graph):
        self.graph = graph
        self.editor = GraphEditor(graph)
        self.adapter = graph.origin_adapter

        self._edge_bindings = dict()
        self._node_bindings = dict()

    def sync(self):
        if self.adapter is None:
            return

        incoming = self.adapter.build_graph(
            directed=self.graph.directed
        )

        self.sync_graph(incoming)
        self.sync_bound_attributes()

    def sync_graph(self, incoming:Graph):
        # if self.graph == incoming:
        #     return

        add_nodes, rm_nodes, handle_persistent_nodes = self._sync_nodes(incoming)
        add_edges, rm_edges, handle_persistent_edges = self._sync_edges(incoming)

        add_nodes()
        add_edges()

        handle_persistent_nodes()
        handle_persistent_edges()

        rm_edges()
        rm_nodes()

    def _sync_nodes(self, incoming:Graph):
        old_nodes = set(self.graph.nodes)
        new_nodes = set(incoming.nodes)

        added_nodes = new_nodes - old_nodes
        removed_nodes = old_nodes - new_nodes
        unchanged_nodes = old_nodes & new_nodes

        # add new nodes
        def add_missing_nodes():
            for node_id in added_nodes:
                self.editor.add_node(
                    incoming.nodes[node_id]
                )

        # remove removed nodes
        def remove_missing_nodes():
            for node_id in removed_nodes:
                self.editor.remove_node(node_id)

        # keep unchanged nodes
        def handle_unchanged_nodes():
            return

        return add_missing_nodes, remove_missing_nodes, handle_unchanged_nodes

    def _sync_edges(self, incoming:Graph):
        old_edges = set(self.graph.edges)
        new_edges = set(incoming.edges)

        added_edge_groups = new_edges - old_edges
        removed_edge_groups = old_edges - new_edges
        unchanged_edge_groups = old_edges & new_edges

        # add new edge groups
        def add_missing_edges():
            for edge_id in added_edge_groups:
                for edge in incoming.edges[edge_id].values():
                    self.editor.add_edge(edge)

        # remove removed edge groups
        def remove_missing_edges():
            for edge_id in removed_edge_groups:
                self.editor.remove_edges_of_id(edge_id)

        # check for changes within persisting edge groups
        def handle_unchanged_edges():
            for edge_id in unchanged_edge_groups:
                edge_group_old = self.graph.edges[edge_id]
                edge_group_new = incoming.edges[edge_id]

                # handle comparisons
                matched_new = set()
                edges_to_remove = []
                edges_to_add = []

                # edges to keep or remove
                for old_uid, old_edge in edge_group_old.items():
                    match = None

                    for new_uid, new_edge in edge_group_new.items():
                        if new_uid in matched_new:
                            continue

                        if self._same_edge(old_edge, new_edge):
                            match = new_uid
                            break

                    if match is not None:
                        matched_new.add(match)
                        old_edge.origin_key = edge_group_new[match].origin_key
                    else:
                        edges_to_remove.append(old_edge)

                # edges to add
                for new_uid, new_edge in edge_group_new.items():
                    if new_uid not in matched_new:
                        edges_to_add.append(new_edge)

                # removing edges
                for edge in edges_to_remove:
                    self.editor.remove_edge(edge, target_exact=True)

                # adding edges
                for edge in edges_to_add:
                    self.editor.add_edge(edge)

        return add_missing_edges, remove_missing_edges, handle_unchanged_edges


    @staticmethod
    def _same_edge(a:Edge, b:Edge):
        # leave out `uid`, `colour`, `attributes`, `origin_id`
        return (
            a.id == b.id
            and a.source == b.source
            and a.target == b.target
            and a.label == b.label
        )


    # Synchronize attributes from user data structures to graph contents
    def sync_bound_attributes(self):
        self.sync_edge_attributes()
        self.sync_node_attributes()

    # synchronize edge attribute sources with user data structures (preserve mutability)
    def bind_edge_attribute(self, key, values):
        self._edge_bindings[key] = values

    # synchronize node attribute sources with user data structures (preserve mutability)
    def bind_node_attribute(self, key, values):
        self._node_bindings[key] = values

    # spread bound containers of attributes across edges
    def sync_edge_attributes(self):
        for edge_group in self.graph.edges.values():
            for edge in edge_group.values():
                for key, attribute in self._edge_bindings.items():
                    edge.attributes[key] = self.adapter.get_edge_attribute(attribute, edge)

    # spread bound containers of attributes across nodes
    def sync_node_attributes(self):
        for node in self.graph.nodes.values():
            for key, attribute in self._node_bindings.items():
                node.attributes[key] = self.adapter.get_node_attribute(attribute, node)

    def clear_bindings(self):
        ...



