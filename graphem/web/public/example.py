"""
    Hii! Welcome to GraphEm :)
    Write whatever python code you'd like in here,
    you can execute it and use the GraphEm library
    to visualize whatever graphology you desire B]

    The script entry point `app.run()` is executed by the application
    when you press the `Run` button, so do not add it yourself!

    The following is a simple example script as a demonstration:
"""


# Imports
from graphem.adapters.edge_list import EdgeListAdapter
from graphem.frontends.web import WebApp
from graphem.core.edge import Edge
from graphem.core.node import Node
from graphem.core.colour import Colour


# A simple recursive dfs traversal with steps every loop iteration
async def mycode(app:WebApp):
    await app.step()

    visited_nodes = [False] * n_nodes
    visited_edges = [False] * len(edges)

    app.set_edge_attribute("visited", visited_edges)
    app.set_node_attribute("visited", visited_nodes)

    async def dfs(node):
        print(f"visiting node {node}")
        visited_nodes[node] = True
        await app.step()

        outgoing_edges = [(e, edge) for e, edge in enumerate(edges) if node in edge and not visited_edges[e]]
        for e, edge in outgoing_edges:
            visited_edges[e] = True
            await app.step()

            node1, node2 = edge
            if not visited_nodes[node1]:
                await dfs(node1)
            elif not visited_nodes[node2]:
                await dfs(node2)

    await dfs(0)


# Rendering method overridez, that mark visited nodes/edges
def get_edge_colour(edge:Edge) -> Colour:
    visited = edge.attributes.get("visited", None)

    if visited is None:
        return Colour(60, 60, 60)

    return Colour(50, 150, 50) if visited else Colour(30, 30, 30)

def get_node_colour(node:Node) -> Colour:
    visited = node.attributes.get("visited", None)

    if visited is None:
        return Colour(60, 60, 60)

    return Colour(50, 150, 50) if visited else Colour(150, 50, 50)


# Graph structure
edges = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (4, 5), (5, 6), (6, 7), (7, 8),
    (8, 9), (9, 10), (10, 11), (11, 12),
    (12, 13), (13, 14), (14, 15), (15, 16),
    (16, 17), (17, 18), (18, 19), (19, 0),

    (0, 5), (0, 8), (0, 13),
    (1, 6), (1, 11),
    (2, 7), (2, 15),
    (3, 9), (3, 17),
    (4, 10), (4, 18),

    (5, 12), (5, 16),
    (6, 13), (6, 19),
    (7, 14), (7, 18),
    (8, 15), (8, 19),
    (9, 16), (9, 12),

    (10, 17), (10, 14),
    (11, 18), (11, 15),
    (12, 19), (12, 16),
    (13, 17), (14, 19),
    (2, 18)
]
n_nodes = 20

# Loading the graph into Graphem library
graph = EdgeListAdapter(edges).build_graph()    # build graph from given structure in EdgeList format

# Setup
app = WebApp(graph, user_script=mycode)     # execute mycode()
app.set_get_edge_colour(get_edge_colour)    # use get_edge_colour() for rendering edges
app.set_get_node_colour(get_node_colour)    # use get_node_colour() for rendering nodes
