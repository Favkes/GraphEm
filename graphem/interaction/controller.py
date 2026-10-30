from collections.abc import Hashable
from enum import Enum

from ..core.position import Position, ttop
from ..core.graph import Graph
from ..core.node import Node


# chuj dupa i kamieni kupa - Szymon


class DragMode(Enum):
    NONE = None
    SELECTION = "selection"
    MOVE_NODES = "move_nodes"


class GraphController:
    graph:Graph
    selected_nodes:set[Hashable]    # set of node id's

    mouse_down_pos:Position|None
    last_mouse_pos:Position|None
    dragging:bool
    drag_mode:DragMode|None


    def __init__(self, graph:Graph):
        self.graph = graph
        self.selected_nodes = set()

        self.mouse_down_pos = None
        self.last_mouse_pos = None
        self.dragging = False
        self.drag_mode = DragMode.NONE

    def mouse_down(self,
                   pos:Position|tuple[float,float],
                   button:int,
                   shift:bool = False):
        pos = ttop(pos)

        self.mouse_down_pos = pos

        node_id = self.get_node_at(pos)
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


    def mouse_move(self, pos:Position|tuple[float,float]):
        pos = ttop(pos)

        if self.last_mouse_pos is None:
            self.last_mouse_pos = pos

        if self.mouse_down_pos:
            self.dragging = True

        if self.dragging:
            if self.drag_mode == DragMode.MOVE_NODES:
                self._drag_nodes(pos)

        self.last_mouse_pos = pos

    def mouse_up(self,
                 pos:Position|tuple[float,float],
                 button:int,
                 shift:bool = False):
        pos = ttop(pos)

        if self.dragging:
            if self.drag_mode == DragMode.SELECTION:
                sel_from, sel_to = self.mouse_down_pos, pos

                if not shift:
                    self.selected_nodes.clear()

                for node_id in self.get_nodes_in(sel_from, sel_to):
                    self.selected_nodes.add(node_id)
        else:
            self.selected_nodes.clear()

        self.mouse_down_pos = None
        self.dragging = False
        self.drag_mode = DragMode.NONE

    def get_node_at(self, pos:Position|tuple[float,float]) -> Hashable|None:
        pos = ttop(pos)

        for node_id, node in self.graph.nodes.items():
            if (node.pos.x - pos.x)**2 + (node.pos.y - pos.y)**2 <= node.radius**2:
                return node_id
        return None

    def get_nodes_in(self, pos_from:Position|tuple[float,float], pos_to:Position|tuple[float,float]):
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


