import cv2
import numpy as np


X, Y = 500, 500


class Graph:
    V:          int
    E:          int
    vertices:   list
    edges:      list
    matrix:     np.array
    _varname:   str

    def __init__(self):
        self.E          = 0
        self.V          = 0
        self.vertices   = []
        self.edges      = []
        self.matrix     = None
        self._varname   = None

    def _saymyname(self):
        for name, obj in globals().items():
            if obj is self:
                self._varname = name

    def __str__(self):
        if self._varname is None: self._saymyname()
        self.V = len(self.vertices)
        self.E = len(self.edges)
        out = f"Graph {self._varname} {{\n   E = {self.E}\n   V = {self.V}\n   v = {self.edges}\n}}"
        return out

    def generate_matrix(self):
        matrix = np.zeros((self.V, self.V), np.uint16)
        for edge in self.edges:
            a, b = edge
            matrix[a, b] = 1
            matrix[b, a] = 1
        self.matrix = matrix


def distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return dx*dx + dy*dy


def mouse_callback(event, x, y, flags, param):
    global pendown_x, pendown_y, penstart_x, penstart_y, is_pen_down, g1, snap_to, start_snap, end_snap
    global mouse_2_point_offset_x, mouse_2_point_offset_y, moving_point
    pendown_x, pendown_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        if is_pen_down:
            pt1, pt2 = (penstart_x, penstart_y), (pendown_x, pendown_y)
            v_count = len(g1.vertices)

            if snap_to is not None:
                end_snap = snap_to

                if start_snap is not None:
                    g1.edges.append((start_snap, end_snap))
                    # pt2 = g1.vertices[snap_to]
                else:
                    g1.vertices.append(pt1)
                    g1.edges.append((v_count, end_snap))
            else:
                if start_snap is not None:
                    g1.vertices.append(pt2)
                    g1.edges.append((start_snap, v_count))
                else:
                    g1.vertices.append(pt1)
                    g1.vertices.append(pt2)
                    g1.edges.append((v_count, v_count + 1))
        else:
            start_snap, end_snap = None, None   # resetting the values

            penstart_x, penstart_y = x, y

            if snap_to is not None:
                start_snap = snap_to
                penstart_x, penstart_y = g1.vertices[snap_to]

        is_pen_down = not is_pen_down

    elif event == cv2.EVENT_RBUTTONDOWN:
        if is_pen_down:
            is_pen_down = False
            start_snap, end_snap = None, None
        else:
            if (snap_to is not None) and (moving_point is None):
                moving_point = snap_to
                tmpx, tmpy = g1.vertices[snap_to]
                mouse_2_point_offset_x = tmpx - pendown_x
                mouse_2_point_offset_y = tmpy - pendown_y

    elif event == cv2.EVENT_RBUTTONUP:
        if (not is_pen_down) and (snap_to is not None):
            moving_point = None
            mouse_2_point_offset_x = None
            mouse_2_point_offset_y = None

    if moving_point is not None:
        g1.vertices[moving_point] = (
            pendown_x + mouse_2_point_offset_x,
            pendown_y + mouse_2_point_offset_y
        )


cv2.namedWindow("Graph builder (alpha)", flags=cv2.WINDOW_NORMAL)
cv2.resizeWindow("Graph builder (alpha)", (X, Y))

pendown_x, pendown_y = 0, 0
penstart_x, penstart_y = 0, 0
is_pen_down = False
snap_to = None
start_snap, end_snap = None, None
mouse_2_point_offset_x, mouse_2_point_offset_y = None, None
moving_point = None
cv2.setMouseCallback("Graph builder (alpha)", mouse_callback)

g1 = Graph()

img = np.zeros((Y, X, 3), np.uint8)
while True:
    snap_to = None
    cv2.imshow("Graph builder (alpha)", img)
    img = np.zeros((Y, X, 3), np.uint8)


    i = -1
    for edge in g1.edges:
        i += 1
        vertex1, vertex2 = g1.vertices[edge[0]], g1.vertices[edge[1]]
        cv2.line(img, pt1=vertex1, pt2=vertex2, color=(200, 200, 23), thickness=1)

        cv2.circle(img, center=vertex1, radius=15, color=(0, 0, 0), thickness=-1)
        cv2.circle(img, center=vertex2, radius=15, color=(0, 0, 0), thickness=-1)

        circle_color = (200, 200, 23)
        if distance(vertex1, (pendown_x, pendown_y)) < 225:
            snap_to = edge[0]               # snap vertex index
            circle_color = (200, 23, 200)
            cv2.circle(img, center=vertex1, radius=15, color=circle_color, thickness=1)
        # cv2.putText(
        #     img, str(i), vertex1, cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 23, 200), 2, cv2.LINE_AA
        # )

        circle_color = (200, 200, 23)
        if distance(vertex2, (pendown_x, pendown_y)) < 225:
            snap_to = edge[1]               # snap vertex index
            circle_color = (200, 23, 200)
            cv2.circle(img, center=vertex2, radius=15, color=circle_color, thickness=1)

    i = -1
    for vertex in g1.vertices:
        i += 1
        x, y = vertex
        cv2.putText(
            img, str(i), (x-7, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 23, 200), 1, cv2.LINE_AA
        )

    if is_pen_down:
        cv2.line(img, pt1=(penstart_x, penstart_y), pt2=(pendown_x, pendown_y), color=(23, 200, 200), thickness=1)

    # print(g1.__dict__)

    keypressed = cv2.waitKey(1) & 0xFF
    if keypressed == ord('q'):
        break
    elif keypressed == ord(' '):
        print(g1)
        g1.generate_matrix()
        print(g1.matrix)
