"""Tests for XinAnKnowledgeGraph."""
import sys
import os

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.models.xinan_kg import XinAnKnowledgeGraph


def test_init_has_seed_data():
    kg = XinAnKnowledgeGraph()
    stats = kg.stats()
    assert stats["nodes"] > 0, "Graph should have seed nodes"
    assert stats["edges"] > 0, "Graph should have seed edges"
    print(f"  [PASS] init: {stats['nodes']} nodes, {stats['edges']} edges")


def test_add_triple():
    kg = XinAnKnowledgeGraph()
    new_edge = kg.add_triple("黄芪", "补气", "功效")
    assert new_edge is True, "New triple should return True"
    # Adding same triple again should return False (already existed)
    dup = kg.add_triple("黄芪", "补气", "功效")
    assert dup is False, "Duplicate triple should return False"
    # Verify it's queryable - query returns (target, relation) tuples
    results = kg.query("黄芪")
    assert any(target == "补气" for target, _ in results), "Should find 补气 as target"
    print("  [PASS] add_triple")


def test_query_existing():
    kg = XinAnKnowledgeGraph()
    results = kg.query("新安医学")
    assert len(results) >= 1, "新安医学 should have outgoing edges"
    targets = [target for target, _ in results]
    assert "汪机" in targets, "汪机 should be reachable from 新安医学"
    print(f"  [PASS] query: found {len(results)} outgoing edges from 新安医学")


def test_query_missing():
    kg = XinAnKnowledgeGraph()
    results = kg.query("不存在的实体")
    assert results == [], "Missing entity should return empty list"
    print("  [PASS] query missing entity returns []")


def test_search():
    kg = XinAnKnowledgeGraph()
    matches = kg.search("医")
    assert len(matches) >= 2, f"Should match multiple entities with '医', got {len(matches)}"
    print(f"  [PASS] search '医': found {matches}")
    # Search for something that doesn't exist
    none_match = kg.search("ZZZZNOTFOUND")
    assert none_match == [], "Nonexistent keyword should return []"
    print("  [PASS] search nonexistent keyword returns []")


def test_get_neighbors():
    kg = XinAnKnowledgeGraph()
    nbrs = kg.get_neighbors("参苓白术散")
    assert len(nbrs["outgoing"]) >= 1, "Should have outgoing edges"
    assert len(nbrs["incoming"]) >= 1, "Should have incoming edges from 汪机"
    print(f"  [PASS] get_neighbors: out={len(nbrs['outgoing'])}, in={len(nbrs['incoming'])}")


def test_export_json():
    import json
    kg = XinAnKnowledgeGraph()
    raw = kg.export_json()
    data = json.loads(raw)
    assert "nodes" in data and "edges" in data, "JSON should have nodes and edges keys"
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0
    print(f"  [PASS] export_json: {len(data['nodes'])} nodes, {len(data['edges'])} edges")


def test_stats():
    kg = XinAnKnowledgeGraph()
    s = kg.stats()
    assert "nodes" in s and "edges" in s and "density" in s
    assert s["density"] > 0
    print(f"  [PASS] stats: {s}")


def run_all():
    tests = [
        test_init_has_seed_data,
        test_add_triple,
        test_query_existing,
        test_query_missing,
        test_search,
        test_get_neighbors,
        test_export_json,
        test_stats,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            failed += 1
    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
