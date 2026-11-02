import asyncio
from collections.abc import Sequence, Hashable
# noinspection PyUnresolvedReferences
from js import document, window
from pyodide.ffi import create_proxy

from graphem.renderers.web import WebRenderer
from graphem.interaction.controller import GraphController, DragMode, ToolMode
from graphem.core.graph import Graph
from graphem.core.sync import GraphSynchronizer
from graphem.core.position import Position


class WebApp:
    def __init__(self, graph:Graph, user_script = None):
        self.graph = graph
        self.controller = GraphController(graph)
        self.synchronizer = GraphSynchronizer(graph)

        self.running = False
        self.canvas = None
        self.ctx = None
        self.renderer = None

        self._user_script = user_script
        self._next_event = asyncio.Event()

        self._edge_colour_fn = None
        self._node_colour_fn = None

        self._proxies = []

    @property
    def user_script(self):
        return self._user_script
    @user_script.setter
    def user_script(self, func):
        self._user_script = func

    @staticmethod
    def _map_mouse_button(js_button:int) ->int:
        return {
            0: 1, # LMB
            1: 2, # MMB
            2: 3  # RMB
        }.get(js_button, js_button)

    def _event_pos(self, event) -> tuple[int,int]:
        rect = self.canvas.getBoundingClientRect()
        x = (event.clientX - rect.left) * self.canvas.width / rect.width
        y = (event.clientY - rect.top) * self.canvas.height / rect.height
        return int(x), int(y)

    def handle_mouse_down(self, event):
        shift = bool(event.shiftKey)
        pos = self._event_pos(event)
        button = self._map_mouse_button(event.button)
        self.controller.mouse_down(pos, button, shift=shift)

    def handle_mouse_move(self, event):
        pos = self._event_pos(event)
        self.controller.mouse_move(pos)

    def handle_mouse_up(self, event):
        shift = bool(event.shiftKey)
        pos = self._event_pos(event)
        button = self._map_mouse_button(event.button)
        self.controller.mouse_up(pos, button, shift=shift)

    def handle_keydown(self, event):
        key = event.key.lower()

        if key == "d":
            if self.controller.active_tool is not ToolMode.NONE:
                self.controller.remove_selected_nodes()
        elif key == "c":
            self.controller.active_tool = ToolMode.CREATE
        elif key == "m":
            self.controller.active_tool = ToolMode.MOVE
        elif key == "p":
            self.controller.active_tool = ToolMode.NONE
        elif key == " ":
            event.preventDefault()
            self._next_event.set()

    # Clear screen and render new frame
    def render_frame(self):
        selection_rect = (
            self.controller.mouse_down_pos,
            self.controller.last_mouse_pos
        ) if self.controller.drag_mode == DragMode.SELECTION else None

        edge_creation_node_positions_list = [
            self.graph.nodes[node_id].pos
            for node_id in self.controller.selected_nodes
        ] if self.controller.drag_mode == DragMode.CREATE_EDGE else None

        self.renderer.draw(self.ctx,
                      self.graph,
                      selected_nodes=self.controller.selected_nodes,
                      selection_rect=selection_rect,
                      edge_creation_nodes=edge_creation_node_positions_list,
                      cursor_position=self.controller.last_mouse_pos
                      )

    # Initialize app
    def open(self):
        self.canvas = document.getElementById("graph-canvas")
        self.ctx = self.canvas.getContext("2d")
        self.renderer = WebRenderer()

        if self._edge_colour_fn:
            self.renderer.set_get_edge_colour(self._edge_colour_fn)
        if self._node_colour_fn:
            self.renderer.set_get_node_colour(self._node_colour_fn)

        def prevent_context_menu(event):
            event.preventDefault()

        for handler, target, event_name in [
            (self.handle_mouse_down, self.canvas, "mousedown"),
            (self.handle_mouse_move, self.canvas, "mousemove"),
            (self.handle_mouse_up, self.canvas, "mouseup"),
            (self.handle_keydown, window, "keydown"),
            (prevent_context_menu, self.canvas, "contextmenu")
        ]:
            proxy = create_proxy(handler)
            target.addEventListener(event_name, proxy)
            self._proxies.append((target, event_name, proxy))

        self.running = True

    # Singular iteration of the main app loop
    def tick(self):
        self.render_frame()

    # Pause user script execution
    async def step(self):
        self.synchronizer.sync_bound_attributes()
        self._next_event.clear()
        await self._next_event.wait()

    # Main App entry point
    async def run(self):
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

            for target, event_name, proxy in self._proxies:
                target.removeEventListener(event_name, proxy)
                proxy.destroy()

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
