import asyncio
from collections.abc import Sequence, Hashable
from enum import Enum
# noinspection PyUnresolvedReferences
from js import document, window, Event
from pyodide.ffi import create_proxy, jsnull
import traceback

from graphem.renderers.web import WebRenderer
from graphem.interaction.controller import GraphController, DragMode, ToolMode
from graphem.core.graph import Graph
from graphem.core.sync import GraphSynchronizer
from graphem.core.position import Position


class UserAction:
    CREATE = "create"
    MOVE = "move"
    NONE = "none"
    DELETE = "delete"
    STEP = "step"


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
        self._script_task = None
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
        if event.target.closest("#python-editor"):
            return  # allow writing whitespaces in editor during execution

        actions = {
            "c": UserAction.CREATE,
            "m": UserAction.MOVE,
            "p": UserAction.NONE,
            "d": UserAction.DELETE,
            " ": UserAction.STEP
        }

        key = str(event.key).lower()

        if key in actions:
            if key == " ":
                event.preventDefault()

            self.handle_command(actions[key])

    def handle_command(self, action:str):
        if action == UserAction.CREATE:
            self.controller.active_tool = ToolMode.CREATE

        elif action == UserAction.MOVE:
            self.controller.active_tool = ToolMode.MOVE

        elif action == UserAction.NONE:
            self.controller.active_tool = ToolMode.NONE

        elif action == UserAction.DELETE:
            if self.controller.active_tool is not ToolMode.NONE:
                self.controller.remove_selected_nodes()

        elif action ==UserAction.STEP:
            self._next_event.set()

        self.update_tool_buttons()

    def handle_button_click(self, event):
        button = event.target.closest("[data-action]")

        if button is None or button is jsnull:
            return

        action = str(button.getAttribute("data-action"))
        self.handle_command(action)

    def update_tool_buttons(self):
        active_action = {
            ToolMode.NONE: UserAction.NONE,
            ToolMode.MOVE: UserAction.MOVE,
            ToolMode.CREATE: UserAction.CREATE,
        }.get(self.controller.active_tool)

        for button in document.querySelectorAll("[data-action]"):
            action = button.getAttribute("data-action")

            if action in (UserAction.NONE, UserAction.MOVE, UserAction.CREATE):
                button.setAttribute(
                    "aria-pressed",
                    "true" if action == active_action else "false"
                )

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

        proxy = create_proxy(self.handle_button_click)
        document.addEventListener("click", proxy)
        self._proxies.append(
            (document, "click", proxy)
        )

        self.update_tool_buttons()

        self.running = True

    # Singular iteration of the main app loop
    def tick(self):
        self.render_frame()

    @property
    def script_finished(self):
        return (
            self._script_task is not None
            and self._script_task.done()
        )

    # Pause user script execution
    async def step(self, block:bool = True):
        self.synchronizer.sync_bound_attributes()
        if block:
            self._next_event.clear()
            await self._next_event.wait()
        else:
            await asyncio.sleep(0)

    # Main App entry point
    async def run(self, exit_after_finish:bool = True):
        self.open()

        self._script_task = None
        if self._user_script is not None:
            self._script_task = asyncio.create_task(self._user_script(self))

            def handle_task_result(finished_task):
                if finished_task.cancelled():
                    return

                error = finished_task.exception()
                if error is not None:
                    traceback.print_exception(error)

                document.dispatchEvent(Event.new("graphem:finished"))

            self._script_task.add_done_callback(handle_task_result)

        try:
            while self.running:
                self.tick()

                if exit_after_finish and self.script_finished:
                    self.running = False

                await asyncio.sleep(1/60)

        finally:
            if self._script_task is not None:
                self._script_task.cancel()
                await asyncio.gather(self._script_task, return_exceptions=True)

            for target, event_name, proxy in self._proxies:
                target.removeEventListener(event_name, proxy)
                proxy.destroy()

            self._proxies.clear()
            self.running = False

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
