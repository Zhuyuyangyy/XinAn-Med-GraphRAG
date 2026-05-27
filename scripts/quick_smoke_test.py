#!/usr/bin/env python3
"""Quick smoke test: build graph, query entities, export JSON."""
import sys
import os
import json

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models.xinan_kg import XinAnKnowledgeGraph


def main():
    print("=" * 60)
    print("XinAn-Med-GraphRAG Quick Smoke Test")
    print("=" * 60)

    # 1. Build graph
    print("\n[1] Building knowledge graph...")
    kg = XinAnKnowledgeGraph()
    s = kg.stats()
    print(f"    Nodes: {s['nodes']}, Edges: {s['edges']}, Density: {s['density']}")

    # 2. Add custom triples
    print("\n[2] Adding custom triples...")
    triples = [
        ("新安医学", "新安培元", "学术流派"),
        ("新安培元", "培元固本", "核心理念"),
        ("程国彭", "八法", "学术贡献"),
        ("八法", "汗法", "组成"),
        ("八法", "吐法", "组成"),
        ("八法", "下法", "组成"),
        ("八法", "和法", "组成"),
    ]
    added = 0
    for subj, obj, rel in triples:
        if kg.add_triple(subj, obj, rel):
            added += 1
    print(f"    Added {added} new triples")

    # 3. Query entities
    print("\n[3] Querying entities...")
    for entity in ["新安医学", "汪机", "程国彭", "参苓白术散"]:
        results = kg.query(entity)
        if results:
            print(f"    {entity} ->")
            for target, rel in results:
                print(f"      - [{rel}] {target}")

    # 4. Search
    print("\n[4] Searching for '医'...")
    matches = kg.search("医")
    print(f"    Matches: {matches}")

    print("\n[5] Searching for '法'...")
    matches = kg.search("法")
    print(f"    Matches: {matches}")

    # 5. Neighbors
    print("\n[6] Full neighbor info for '八法'...")
    nbrs = kg.get_neighbors("八法")
    for e in nbrs["outgoing"]:
        print(f"    -> [{e['relation']}] {e['target']}")
    for e in nbrs["incoming"]:
        print(f"    <- [{e['relation']}] {e['source']}")

    # 6. Export JSON
    print("\n[7] Exporting graph to JSON...")
    json_str = kg.export_json()
    out_path = os.path.join(os.path.dirname(__file__), "..", "graph_export.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json_str)
    data = json.loads(json_str)
    print(f"    Exported {len(data['nodes'])} nodes, {len(data['edges'])} edges")
    print(f"    Saved to: {out_path}")

    # Final stats
    print("\n[8] Final graph stats:")
    final = kg.stats()
    for k, v in final.items():
        print(f"    {k}: {v}")

    print("\n" + "=" * 60)
    print("SMOKE TEST PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
