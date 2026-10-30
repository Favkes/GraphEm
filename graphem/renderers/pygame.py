from collections.abc import Hashable
from math import hypot
import pygame

from ..core.graph import Graph
from ..core.colour import Colour
from ..core.position import Position


class PygameRenderer:
    def __init__(self, edge_width=2):
        self.edge_width = edge_width
        self.font = pygame.font.Font(None, 24)

    def draw(self,
             surface:pygame.surface,
             graph:Graph,
             selected_nodes:set[Hashable] = None,
             selection_rect:tuple[Position,Position] = None) -> None:

        border_colour = Colour(200, 150, 100)
        selected_colour = Colour(220, 220, 255)
        selection_border_col = Colour(80, 80, 150)
        selection_inside_col = Colour(20, 20, 50)
        line_colour = Colour(70, 160, 100)

        if selection_rect:
            rect_from, rect_to = selection_rect

            rect = pygame.Rect(
                rect_from.x,
                rect_from.y,
                rect_to.x - rect_from.x,
                rect_to.y - rect_from.y
            )
            rect.normalize()

            pygame.draw.rect(
                surface,
                selection_inside_col.val,
                rect
            )
            pygame.draw.rect(
                surface,
                selection_border_col.val,
                rect,
                2
            )

        for node in graph.nodes.values():
            pygame.draw.circle(
                surface,
                border_colour.val,
                node.pos.val,
                node.radius,
                3
            )

        if selected_nodes:
            for node_id in selected_nodes:
                node = graph.nodes[node_id]
                pygame.draw.circle(
                    surface,
                    selected_colour.val,
                    node.pos.val,
                    node.radius + 2,
                    1
                )

        for edge_group in graph.edges.values():
            for edge in edge_group.values():
                pygame.draw.line(
                    surface,
                    line_colour.val,
                    graph.nodes.get(edge.source).pos.val,
                    graph.nodes.get(edge.target).pos.val,
                    self.edge_width
                )
