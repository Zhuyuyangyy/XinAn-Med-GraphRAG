"""GraphRAG Engine - Retrieve-and-Generate pipeline combining BM25 + graph context."""
import math
import re
from collections import Counter
from typing import Optional
from backend.models.xinan_kg import XinAnKnowledgeGraph


class BM25Index:
    """Lightweight BM25 scorer over a list of text documents."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: list[list[str]] = []
        self.doc_ids: list[str] = []
        self.doc_len: list[int] = []
        self.avg_dl: float = 0.0
        self.df: Counter = Counter()
        self.N: int = 0

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Split on non-alphanumeric + keep CJK single chars."""
        tokens = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]+', text.lower())
        return tokens

    def add(self, doc_id: str, text: str):
        tokens = self._tokenize(text)
        self.docs.append(tokens)
        self.doc_ids.append(doc_id)
        self.doc_len.append(len(tokens))
        seen = set(tokens)
        for t in seen:
            self.df[t] += 1
        self.N += 1
        self.avg_dl = sum(self.doc_len) / self.N if self.N else 0

    def score(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self.N == 0:
            return []
        tokens = self._tokenize(query)
        scores: list[tuple[str, float]] = []
        for idx, doc_tokens in enumerate(self.docs):
            tf = Counter(doc_tokens)
            dl = self.doc_len[idx]
            s = 0.0
            for t in tokens:
                if t not in tf:
                    continue
                n_t = self.df.get(t, 0)
                idf = math.log((self.N - n_t + 0.5) / (n_t + 0.5) + 1)
                tf_val = (tf[t] * (self.k1 + 1)) / (tf[t] + self.k1 * (1 - self.b + self.b * dl / (self.avg_dl or 1)))
                s += idf * tf_val
            if s > 0:
                scores.append((self.doc_ids[idx], s))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class GraphRAGEngine:
    """Retrieve-and-Generate pipeline for XinAn medical knowledge."""

    def __init__(self, kg: Optional[XinAnKnowledgeGraph] = None):
        self.kg = kg or XinAnKnowledgeGraph()
        self.bm25 = BM25Index()
        self._build_index()

    def _build_index(self):
        """Index every edge triple and node name for BM25 retrieval."""
        for u, v, d in self.kg.graph.edges(data=True):
            rel = d.get("relation", "")
            text = f"{u} {rel} {v}"
            edge_id = f"{u}->{v}"
            self.bm25.add(edge_id, text)
        # Also index standalone node names
        for node in self.kg.graph.nodes:
            self.bm25.add(f"node:{node}", node)

    def retrieve(self, query: str, top_k: int = 8) -> list[dict]:
        """BM25 retrieve relevant triples, then expand with graph neighbors."""
        bm25_hits = self.bm25.score(query, top_k=top_k)
        seen_entities: set[str] = set()
        context_triples: list[dict] = []

        for doc_id, sc in bm25_hits:
            if doc_id.startswith("node:"):
                entity = doc_id[5:]
                seen_entities.add(entity)
            elif "->" in doc_id:
                parts = doc_id.split("->", 1)
                subj, obj = parts[0], parts[1]
                edge_data = self.kg.graph.get_edge_data(subj, obj) or {}
                rel = edge_data.get("relation", "")
                context_triples.append({"subject": subj, "relation": rel, "object": obj, "score": sc})
                seen_entities.update([subj, obj])

        # Graph expansion: 1-hop neighbors of matched entities
        for entity in list(seen_entities):
            neighbors = self.kg.get_neighbors(entity)
            for edge in neighbors["outgoing"]:
                context_triples.append({
                    "subject": entity, "relation": edge["relation"],
                    "object": edge["target"], "score": 0.1
                })
            for edge in neighbors["incoming"]:
                context_triples.append({
                    "subject": edge["source"], "relation": edge["relation"],
                    "object": entity, "score": 0.1
                })

        # Deduplicate
        dedup: dict[str, dict] = {}
        for t in context_triples:
            key = f"{t['subject']}|{t['relation']}|{t['object']}"
            if key not in dedup or t["score"] > dedup[key]["score"]:
                dedup[key] = t
        results = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)
        return results[:top_k * 3]

    def generate(self, query: str, context_triples: list[dict]) -> str:
        """Synthesize an answer from retrieved triples (template-based, no LLM needed)."""
        if not context_triples:
            return f"未找到与「{query}」相关的知识图谱信息。"

        lines = [f"根据新安医学知识图谱，关于「{query}」的相关信息如下：\n"]
        for i, t in enumerate(context_triples[:10], 1):
            lines.append(f"  {i}. {t['subject']} —[{t['relation']}]→ {t['object']}")
        lines.append(f"\n共检索到 {len(context_triples)} 条相关三元组。")
        return "\n".join(lines)

    def query(self, question: str, top_k: int = 8) -> dict:
        """Full RAG pipeline: retrieve -> generate."""
        triples = self.retrieve(question, top_k=top_k)
        answer = self.generate(question, triples)
        return {
            "question": question,
            "answer": answer,
            "context_triples": triples,
            "triple_count": len(triples),
        }
