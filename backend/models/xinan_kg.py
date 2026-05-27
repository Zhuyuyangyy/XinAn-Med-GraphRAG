"""XinAn Knowledge Graph."""
import networkx as nx

class XinAnKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.graph.add_edge("新安医学", "汪机", relation="代表医家")
        self.graph.add_edge("汪机", "参苓白术散", relation="常用方")
    def query(self, entity):
        if entity in self.graph:
            return [(t, self.graph[entity][t]["relation"]) for t in self.graph.successors(entity)]
        return []
