# noinspection PyUnresolvedReferences
from js import document
from collections.abc import Hashable
from math import pi

from graphem.core.node import Node
from graphem.core.edge import Edge
from graphem.core.graph import Graph
from graphem.core.colour import Colour, to_css
from graphem.core.position import Position


class WebRenderer:
    def __init__(self, edge_width=2):
        self.edge_width = edge_width

    def draw(self,
             ctx,
             graph:Graph,
             selected_nodes: set[Hashable] = None,
             selection_rect: tuple[Position, Position] = None,
             edge_creation_nodes: list[Position] = None,
             cursor_position: Position = None) -> None:
        border_colour = Colour(200, 150, 100)
        selected_colour = Colour(220, 220, 255)
        selection_border_col = Colour(80, 80, 150)
        selection_inside_col = Colour(20, 20, 50)
        line_colour = Colour(70, 160, 100)

        canvas = ctx.canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        if selection_rect:
            rect_from, rect_to = selection_rect
            x = min(rect_from.x, rect_to.x)
            y = min(rect_from.y, rect_to.y)
            w = abs(rect_to.x - rect_from.x)
            h = abs(rect_to.y - rect_from.y)

            ctx.fillStyle = to_css(selection_inside_col)
            ctx.fillRect(x, y, w, h)

            ctx.strokeStyle = to_css(selection_border_col)
            ctx.lineWidth = 2
            ctx.strokeRect(x, y, w, h)


        for edge_group in graph.edges.values():
            for edge in edge_group.values():
                source = graph.nodes[edge.source]
                target = graph.nodes[edge.target]

                ctx.beginPath()
                ctx.strokeStyle = to_css(self._get_edge_colour(edge))
                ctx.lineWidth = self.edge_width
                ctx.moveTo(source.pos.x, source.pos.y)
                ctx.lineTo(target.pos.x, target.pos.y)
                ctx.stroke()

        for node in graph.nodes.values():
            ctx.beginPath()
            ctx.fillStyle = to_css(self._get_node_colour(node))
            ctx.arc(node.pos.x, node.pos.y, node.radius, 0, 2*pi)
            ctx.fill()

        if selected_nodes:
            for node_id in selected_nodes:
                node = graph.nodes[node_id]
                ctx.beginPath()
                ctx.strokeStyle = to_css(selected_colour)
                ctx.lineWidth = 1
                ctx.arc(node.pos.x, node.pos.y, node.radius + 2, 0, 2*pi)
                ctx.stroke()

        if edge_creation_nodes:
            ctx.strokeStyle = to_css(line_colour)
            ctx.lineWidth = self.edge_width

            for nodepos in edge_creation_nodes:
                ctx.beginPath()
                ctx.moveTo(nodepos.x, nodepos.y)
                ctx.lineTo(cursor_position.x, cursor_position.y)
                ctx.stroke()

    @staticmethod
    def _get_edge_colour(edge:Edge) -> Colour:
        return edge.colour
    def set_get_edge_colour(self, fun):
        self._get_edge_colour = fun

    @staticmethod
    def _get_node_colour(node:Node) -> Colour:
        return node.colour
    def set_get_node_colour(self, fun):
        self._get_node_colour = fun

