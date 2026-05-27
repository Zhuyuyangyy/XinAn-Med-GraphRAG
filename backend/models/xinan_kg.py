"""XinAn Knowledge Graph - 新安医学知识图谱."""
import json
import networkx as nx


class XinAnKnowledgeGraph:
    """Knowledge graph for XinAn Traditional Chinese Medicine."""

    def __init__(self):
        self.graph = nx.DiGraph()
        # Seed with core XinAn medical knowledge
        self._seed_data()

    def _seed_data(self):
        """Load initial seed triples into the graph."""
        seeds = [
            ("新安医学", "汪机", "代表医家"),
            ("汪机", "参苓白术散", "常用方"),
            ("新安医学", "程国彭", "代表医家"),
            ("程国彭", "医学心悟", "著作"),
            ("新安医学", "吴谦", "代表医家"),
            ("吴谦", "医宗金鉴", "著作"),
            ("参苓白术散", "人参", "组成"),
            ("参苓白术散", "白术", "组成"),
            ("参苓白术散", "茯苓", "组成"),
        ]
        for subj, obj, rel in seeds:
            self.add_triple(subj, obj, rel)

    def add_triple(self, subject: str, obj: str, relation: str) -> bool:
        """Add a (subject)-[relation]->(object) triple to the graph.

        Returns True if a new edge was created, False if it already existed.
        """
        existed = self.graph.has_edge(subject, obj)
        self.graph.add_edge(subject, obj, relation=relation)
        return not existed

    def query(self, entity: str) -> list:
        """Return outgoing edges from entity as [(target, relation), ...]."""
        if entity in self.graph:
            return [
                (t, self.graph[entity][t]["relation"])
                for t in self.graph.successors(entity)
            ]
        return []

    def search(self, keyword: str) -> list:
        """Search for entities whose name contains the keyword.

        Returns list of matching node names.
        """
        return [node for node in self.graph.nodes if keyword in node]

    def get_neighbors(self, entity: str) -> dict:
        """Return both outgoing and incoming edges for an entity."""
        result = {"outgoing": [], "incoming": []}
        if entity not in self.graph:
            return result
        for target in self.graph.successors(entity):
            rel = self.graph[entity][target]["relation"]
            result["outgoing"].append({"target": target, "relation": rel})
        for source in self.graph.predecessors(entity):
            rel = self.graph[source][entity]["relation"]
            result["incoming"].append({"source": source, "relation": rel})
        return result

    def export_json(self) -> str:
        """Export the graph as a JSON string with nodes and edges."""
        data = {
            "nodes": list(self.graph.nodes),
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "relation": d.get("relation", ""),
                }
                for u, v, d in self.graph.edges(data=True)
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def stats(self) -> dict:
        """Return basic graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": round(nx.density(self.graph), 4),
        }
