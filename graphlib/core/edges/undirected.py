from base import EdgePolicy


class EdgePolicyUndirected(EdgePolicy):
    def add_edge(self, storage, u, v, weight=1):
        ...