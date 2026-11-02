import { loadPyodide } from
    "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";


async function main() {
    const pyodide = await loadPyodide();
    
    document.getElementById("loading").remove();
    console.log("Pyodide initialized.");

    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");

    const wheelUrl = new URL("../../dist/graphem-0.1.1-py3-none-any.whl", import.meta.url).href;
    await micropip.install(wheelUrl);

    console.log("GraphEm installed! ;)");

    await pyodide.runPythonAsync(`
        from graphem.adapters.edge_list import EdgeListAdapter
        from graphem.frontends.web import WebApp
        from graphem.core.edge import Edge
        from graphem.core.node import Node
        from graphem.core.colour import Colour

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

        graph = EdgeListAdapter(edges).build_graph()







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


        app = WebApp(graph, user_script=mycode)
        app.set_get_edge_colour(get_edge_colour)

        await app.run()
    `);
}

// entry point
main();
