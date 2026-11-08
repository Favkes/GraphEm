import pygame
import asyncio
from collections.abc import Sequence, Hashable

from graphem.renderers.pygame import PygameRenderer
from graphem.interaction.controller import GraphController, DragMode, ToolMode
from graphem.core.graph import Graph
from graphem.core.sync import GraphSynchronizer
from graphem.core.position import Position


class App:
    def __init__(self, graph:Graph, user_script = None):
        self.graph = graph
        self.controller = GraphController(graph)
        self.synchronizer = GraphSynchronizer(graph)

        self.dimensions = Position(500, 500)

        self.running = False
        self.screen = None
        self.renderer = None
        self.clock = None

        self._user_script = user_script
        self._next_event = asyncio.Event()

        self._edge_colour_fn = None
        self._node_colour_fn = None

    @property
    def user_script(self):
        return self._user_script
    @user_script.setter
    def user_script(self, func):
        self._user_script = func

    # Handle pygame events
    def handle_event(self, event:pygame.event):
        shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)

        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.controller.mouse_down(event.pos, event.button,
                                       shift=shift)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.controller.mouse_up(event.pos, event.button,
                                     shift=shift)

        elif event.type == pygame.MOUSEMOTION:
            self.controller.mouse_move(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                if self.controller.active_tool is not ToolMode.NONE:
                    self.controller.remove_selected_nodes()

            elif event.key == pygame.K_c:
                self.controller.active_tool = ToolMode.CREATE

            elif event.key == pygame.K_m:
                self.controller.active_tool = ToolMode.MOVE

            elif event.key == pygame.K_p:
                self.controller.active_tool = ToolMode.NONE

            elif event.key == pygame.K_SPACE:
                self._next_event.set()

    # Clear screen and render new frame
    def render_frame(self):
        self.screen.fill((0, 0, 0))

        selection_rect = (self.controller.mouse_down_pos, self.controller.last_mouse_pos) \
            if self.controller.drag_mode == DragMode.SELECTION \
            else None

        edge_creation_node_positions_list = [
            self.graph.nodes[node_id].pos
            for node_id in self.controller.selected_nodes
        ] if self.controller.drag_mode == DragMode.CREATE_EDGE else None

        self.renderer.draw(self.screen,
                      self.graph,
                      selected_nodes=self.controller.selected_nodes,
                      selection_rect=selection_rect,
                      edge_creation_nodes=edge_creation_node_positions_list,
                      cursor_position=self.controller.last_mouse_pos
                      )

    # Initialize app
    def open(self):
        pygame.init()

        width, height = (500, 500)
        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("GraphEm 3.0")

        self.renderer = PygameRenderer()
        if self._edge_colour_fn:
            self.renderer.set_get_edge_colour(self._edge_colour_fn)
        if self._node_colour_fn:
            self.renderer.set_get_node_colour(self._node_colour_fn)

        self.clock = pygame.time.Clock()
        self.running = True

    # Singular iteration of the main app loop
    def tick(self):
        for event in pygame.event.get():
            self.handle_event(event)

        self.render_frame()

        pygame.display.flip()
        # self.clock.tick(60)

    # Pause user script execution
    async def step(self, block: bool = True):
        self.synchronizer.sync_bound_attributes()
        if block:
            self._next_event.clear()
            await self._next_event.wait()
        else:
            await asyncio.sleep(0)

    # App entry point
    def run(self):
        asyncio.run(self._run_async())

    # Main app loop
    async def _run_async(self):
        self.open()

        task = None
        if self._user_script is not None:
            task = asyncio.create_task(self._user_script(self))

        try:
            while self.running:
                self.tick()
                await asyncio.sleep(1/60)
        finally:
            if task is not None:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

            pygame.quit()

    def set_edge_attribute(self, key:Hashable, attr_arr:Sequence,
                           default = None, factory = None):
        self.synchronizer.bind_edge_attribute(key, attr_arr)

    def set_node_attribute(self, key:Hashable, attr_arr:Sequence,
                           default = None, factory = None):
        self.synchronizer.bind_node_attribute(key, attr_arr)

    def sync_graph(self):
        self.synchronizer.sync_graph(self.graph)

    def set_get_edge_colour(self, fun):
        self._edge_colour_fn = fun
        if self.renderer is not None:
            self.renderer.set_get_edge_colour(fun)

    def set_get_node_colour(self, fun):
        self._node_colour_fn = fun
        if self.renderer is not None:
            self.renderer.set_get_node_colour(fun)
