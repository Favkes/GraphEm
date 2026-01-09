from abc import ABC, abstractmethod


class EdgePolicy(ABC):
    @abstractmethod
    def add_edge(self, storage, u, v, weight=1):
        """ Adds an edge to storage acc. to the policy.

        storage - object containing the topology (AdjacencyList)
        u, v    - nodes (vertices)
        weight  - optional edge weight
        """
        pass
