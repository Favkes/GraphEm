from base import EdgePolicy


class EdgePolicyDirected(EdgePolicy):
    def add_edge(self, storage, u, v, weight=1):
        ...