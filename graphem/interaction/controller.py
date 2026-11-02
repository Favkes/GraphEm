from collections.abc import Hashable
from enum import Enum

from ..core.position import Position, ttop, postuple
from ..core.graph import Graph
from ..core.node import Node
from ..core.edge import Edge
from ..core.editor import GraphEditor


# chuj dupa i kamieni kupa - Szymon


class DragMode(Enum):
    NONE = None
    SELECTION = "selection"
    MOVE_NODES = "move_nodes"
    CREATE_EDGE = "create_edge"

class ToolMode(Enum):
    NONE = None
    MOVE = "move"
    CREATE = "create"
    DELETE = "delete"


class GraphController:
    graph:Graph
    selected_nodes:set[Hashable]    # set of node id's

    mouse_down_pos:Position|None
    last_mouse_pos:Position|None
    dragging:bool
    drag_mode:DragMode
    active_tool:ToolMode

    edge_creation_destination:Position|None
    creating_edge:bool


    def __init__(self, graph:Graph):
        self.graph = graph
        self.selected_nodes = set()

        self.mouse_down_pos = None
        self.last_mouse_pos = None
        self.dragging = False
        self.drag_mode = DragMode.NONE
        self.active_tool = ToolMode.MOVE

        self.edge_creation_destination = None

    def mouse_down(self,
                   pos:Position|postuple,
                   button:int,
                   shift:bool = False):
        pos = ttop(pos)

        if self.active_tool == ToolMode.NONE:
            return

        self.mouse_down_pos = pos
        self.last_mouse_pos = pos

        # Node under cursor right now
        node_id = self.get_node_at(pos)

        # if creating node -> create new node under cursor, and let it get dragged with the MOVE tool logic
        if self.active_tool == ToolMode.CREATE:

            # RMB
            if button == 3:
                if node_id is not None:
                    self.select_node(node_id, shift)

                # create a node at cursor position.
                new_node_id = self.create_new_node(pos)

                # if any nodes were selected -> create edges between them and the newly created node
                if bool(self.selected_nodes):
                    editor = GraphEditor(self.graph)

                    for selected_node_id in self.selected_nodes:
                        source, target = selected_node_id, new_node_id
                        # don't add self-edges
                        if source == target: continue
                        editor.add_edge(
                            Edge(
                                id=(source, target),
                                source=source,
                                target=target
                            )
                        )

                # capture selection by new node
                self.select_node(new_node_id)
                node_id = new_node_id


            # LMB
            elif button == 1 and node_id is not None:
                # if creating edge -> open new edge routine and skip the MOVE tool logic
                self.select_node(node_id, shift)

                self.edge_creation_destination = pos
                self.drag_mode = DragMode.CREATE_EDGE
                return

        # -- ToolMode.MOVE:
        if node_id is None:
            # click empty space -> clear selection
            # self.selected_nodes.clear()
            self.drag_mode = DragMode.SELECTION

        else:
            self.drag_mode = DragMode.MOVE_NODES
            if not shift:
                # click focused node without shift -> drag entire focus
                if node_id in self.selected_nodes:
                    return
                # click unfocused node without shift -> clear focus and focus singular node
                self.selected_nodes.clear()
            # click unfocused node with shift -> add node to focus
            self.selected_nodes.add(node_id)


    def mouse_move(self, pos:Position|postuple):
        pos = ttop(pos)

        if self.active_tool == ToolMode.NONE:
            return

        if self.active_tool == ToolMode.CREATE:
            if self.drag_mode == DragMode.CREATE_EDGE:
                # snap to pointed node to show which will be targetted at submit
                node_id = self.get_node_at(pos)
                if node_id is not None:
                    self.edge_creation_destination = self.graph.nodes[node_id].pos
                else:
                    self.edge_creation_destination = pos

        # -- ToolMode.MOVE:
        if self.last_mouse_pos is None:
            self.last_mouse_pos = pos

        if self.mouse_down_pos:
            self.dragging = True

        if self.dragging:
            if self.drag_mode == DragMode.MOVE_NODES:
                self._drag_nodes(pos)

        self.last_mouse_pos = pos

    def mouse_up(self,
                 pos:Position|postuple,
                 button:int,
                 shift:bool = False):
        pos = ttop(pos)

        if self.active_tool == ToolMode.NONE:
            return

        # if drag
        if self.dragging:
            if self.drag_mode == DragMode.CREATE_EDGE:
                node_id = self.get_node_at(pos)
                if node_id is not None:
                    editor = GraphEditor(self.graph)

                    for source_node in self.selected_nodes:
                        source, target = source_node, node_id
                        editor.add_edge(
                            Edge(
                                id=(source, target),
                                source=source,
                                target=target
                            )
                        )

            if self.drag_mode == DragMode.SELECTION:
                sel_from, sel_to = self.mouse_down_pos, pos

                if not shift:
                    self.selected_nodes.clear()

                for node_id in self.get_nodes_in(sel_from, sel_to):
                    self.selected_nodes.add(node_id)

        # if click
        else:
            if self.drag_mode == DragMode.SELECTION and not shift:
                self.selected_nodes.clear()

        self.mouse_down_pos = None
        self.dragging = False
        self.drag_mode = DragMode.NONE

        self.edge_creation_destination = None

    def select_node(self, node_id:Hashable, shift:bool = False):
        # handle node selection with shift option
        if not shift and node_id not in self.selected_nodes:
            self.selected_nodes.clear()
        self.selected_nodes.add(node_id)

    def remove_selected_nodes(self):
        editor = GraphEditor(self.graph)

        for node_id in self.selected_nodes:
            editor.remove_node(node_id)

            for edge_group_key in list(self.graph.edges):
                if node_id in edge_group_key:
                    editor.remove_edges_of_id(edge_group_key)

        self.selected_nodes.clear()

    def create_new_node(self,
                        pos:Position|postuple,
                        source_id:Hashable|None = None) -> Hashable:
        editor = GraphEditor(self.graph)

        node_id = editor.get_free_node_id()

        editor.add_node(
            Node(node_id, pos=ttop(pos))
        )

        if source_id is not None:
            editor.add_edge(
                Edge(
                    id=(source_id, node_id),
                    source=source_id,
                    target=node_id
                )
            )

        return node_id


    def get_node_at(self, pos:Position|postuple) -> Hashable|None:
        pos = ttop(pos)

        for node_id, node in self.graph.nodes.items():
            if (node.pos.x - pos.x)**2 + (node.pos.y - pos.y)**2 <= node.radius**2:
                return node_id
        return None

    def get_nodes_in(self, pos_from:Position|postuple, pos_to:Position|postuple):
        pos_from, pos_to = ttop(pos_from), ttop(pos_to)

        x_min, x_max = min(pos_from.x, pos_to.x), max(pos_from.x, pos_to.x)
        y_min, y_max = min(pos_from.y, pos_to.y), max(pos_from.y, pos_to.y)

        out_arr = []

        for node_id, node in self.graph.nodes.items():
            if x_min < node.pos.x < x_max \
                    and y_min < node.pos.y < y_max:
                out_arr.append(node_id)
        return out_arr


    def _drag_nodes(self, to_pos:Position):
        # assume dragging is true

        dx = to_pos.x - self.last_mouse_pos.x
        dy = to_pos.y - self.last_mouse_pos.y

        for node_id in self.selected_nodes:
            node = self.graph.nodes[node_id]

            node.pos.x += dx
            node.pos.y += dy

