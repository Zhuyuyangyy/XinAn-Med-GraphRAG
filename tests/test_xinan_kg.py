"""Comprehensive tests for XinAnKnowledgeGraph module."""
import json
import pytest
from backend.models.xinan_kg import XinAnKnowledgeGraph


class TestXinAnKnowledgeGraphInit:
    """Test knowledge graph initialization and seed data."""

    def test_init_creates_graph(self):
        kg = XinAnKnowledgeGraph()
        assert kg.graph is not None
        assert kg.graph.number_of_nodes() > 0

    def test_seed_data_has_minimum_nodes(self):
        kg = XinAnKnowledgeGraph()
        stats = kg.stats()
        assert stats["nodes"] >= 100, f"Expected 100+ nodes, got {stats['nodes']}"

    def test_seed_data_has_minimum_edges(self):
        kg = XinAnKnowledgeGraph()
        stats = kg.stats()
        assert stats["edges"] >= 150, f"Expected 150+ edges, got {stats['edges']}"

    def test_seed_data_has_medical_masters(self):
        kg = XinAnKnowledgeGraph()
        masters = ["汪机", "孙一奎", "程国彭", "吴谦", "叶桂"]
        for master in masters:
            assert master in kg.graph.nodes, f"Master {master} not in graph"

    def test_seed_data_has_formulas(self):
        kg = XinAnKnowledgeGraph()
        formulas = ["参苓白术散", "六味地黄丸", "补中益气汤", "归脾汤"]
        for formula in formulas:
            assert formula in kg.graph.nodes, f"Formula {formula} not in graph"

    def test_seed_data_has_herbs(self):
        kg = XinAnKnowledgeGraph()
        herbs = ["人参", "黄芪", "白术", "茯苓", "甘草"]
        for herb in herbs:
            assert herb in kg.graph.nodes, f"Herb {herb} not in graph"

    def test_seed_data_has_syndromes(self):
        kg = XinAnKnowledgeGraph()
        syndromes = ["脾胃虚弱", "气血两虚", "肝郁脾虚"]
        for syndrome in syndromes:
            assert syndrome in kg.graph.nodes, f"Syndrome {syndrome} not in graph"

    def test_seed_data_has_schools(self):
        kg = XinAnKnowledgeGraph()
        schools = ["培元派", "温补派", "伤寒学派"]
        for school in schools:
            assert school in kg.graph.nodes, f"School {school} not in graph"

    def test_seed_data_has_books(self):
        kg = XinAnKnowledgeGraph()
        books = ["石山医案", "赤水玄珠", "医学心悟", "医宗金鉴"]
        for book in books:
            assert book in kg.graph.nodes, f"Book {book} not in graph"


class TestAddTriple:
    """Test adding triples to the knowledge graph."""

    def test_add_new_triple_returns_true(self):
        kg = XinAnKnowledgeGraph()
        result = kg.add_triple("测试实体A", "测试实体B", "测试关系")
        assert result is True

    def test_add_duplicate_triple_returns_false(self):
        kg = XinAnKnowledgeGraph()
        kg.add_triple("测试实体A", "测试实体B", "测试关系")
        result = kg.add_triple("测试实体A", "测试实体B", "测试关系")
        assert result is False

    def test_add_triple_creates_edge(self):
        kg = XinAnKnowledgeGraph()
        kg.add_triple("实体X", "实体Y", "关系Z")
        assert kg.graph.has_edge("实体X", "实体Y")
        assert kg.graph["实体X"]["实体Y"]["relation"] == "关系Z"

    def test_add_triple_updates_relation(self):
        kg = XinAnKnowledgeGraph()
        kg.add_triple("实体X", "实体Y", "关系A")
        kg.add_triple("实体X", "实体Y", "关系B")
        assert kg.graph["实体X"]["实体Y"]["relation"] == "关系B"


class TestQuery:
    """Test querying entities from the knowledge graph."""

    def test_query_existing_entity(self):
        kg = XinAnKnowledgeGraph()
        results = kg.query("新安医学")
        assert len(results) >= 1
        targets = [target for target, _ in results]
        assert "汪机" in targets

    def test_query_returns_tuples(self):
        kg = XinAnKnowledgeGraph()
        results = kg.query("新安医学")
        for item in results:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_query_missing_entity_returns_empty(self):
        kg = XinAnKnowledgeGraph()
        results = kg.query("不存在的实体")
        assert results == []

    def test_query_formula_has_ingredients(self):
        kg = XinAnKnowledgeGraph()
        results = kg.query("参苓白术散")
        assert len(results) > 0
        targets = [target for target, _ in results]
        assert "人参" in targets

    def test_query_master_has_books(self):
        kg = XinAnKnowledgeGraph()
        results = kg.query("汪机")
        assert len(results) > 0
        targets = [target for target, _ in results]
        assert "石山医案" in targets


class TestSearch:
    """Test searching entities by keyword."""

    def test_search_partial_match(self):
        kg = XinAnKnowledgeGraph()
        matches = kg.search("医")
        assert len(matches) >= 2

    def test_search_exact_match(self):
        kg = XinAnKnowledgeGraph()
        matches = kg.search("汪机")
        assert "汪机" in matches

    def test_search_no_match_returns_empty(self):
        kg = XinAnKnowledgeGraph()
        matches = kg.search("ZZZZNOTFOUND")
        assert matches == []

    def test_search_single_char(self):
        kg = XinAnKnowledgeGraph()
        matches = kg.search("汤")
        assert len(matches) >= 1

    def test_search_herb_name(self):
        kg = XinAnKnowledgeGraph()
        matches = kg.search("人参")
        assert "人参" in matches


class TestGetNeighbors:
    """Test getting neighbor information."""

    def test_get_neighbors_outgoing(self):
        kg = XinAnKnowledgeGraph()
        nbrs = kg.get_neighbors("参苓白术散")
        assert len(nbrs["outgoing"]) >= 1

    def test_get_neighbors_incoming(self):
        kg = XinAnKnowledgeGraph()
        nbrs = kg.get_neighbors("参苓白术散")
        assert len(nbrs["incoming"]) >= 1

    def test_get_neighbors_structure(self):
        kg = XinAnKnowledgeGraph()
        nbrs = kg.get_neighbors("汪机")
        assert "outgoing" in nbrs
        assert "incoming" in nbrs
        for edge in nbrs["outgoing"]:
            assert "target" in edge
            assert "relation" in edge
        for edge in nbrs["incoming"]:
            assert "source" in edge
            assert "relation" in edge

    def test_get_neighbors_missing_entity(self):
        kg = XinAnKnowledgeGraph()
        nbrs = kg.get_neighbors("不存在的实体")
        assert nbrs == {"outgoing": [], "incoming": []}

    def test_get_neighbors_root_node(self):
        kg = XinAnKnowledgeGraph()
        nbrs = kg.get_neighbors("新安医学")
        assert len(nbrs["outgoing"]) >= 10
        assert len(nbrs["incoming"]) == 0


class TestExportJson:
    """Test JSON export functionality."""

    def test_export_json_valid(self):
        kg = XinAnKnowledgeGraph()
        raw = kg.export_json()
        data = json.loads(raw)
        assert "nodes" in data
        assert "edges" in data

    def test_export_json_has_data(self):
        kg = XinAnKnowledgeGraph()
        raw = kg.export_json()
        data = json.loads(raw)
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0

    def test_export_json_edge_structure(self):
        kg = XinAnKnowledgeGraph()
        raw = kg.export_json()
        data = json.loads(raw)
        for edge in data["edges"]:
            assert "source" in edge
            assert "target" in edge
            assert "relation" in edge

    def test_export_json_ensure_ascii(self):
        kg = XinAnKnowledgeGraph()
        raw = kg.export_json()
        assert "汪机" in raw  # Chinese characters should not be escaped


class TestStats:
    """Test statistics functionality."""

    def test_stats_has_required_keys(self):
        kg = XinAnKnowledgeGraph()
        s = kg.stats()
        assert "nodes" in s
        assert "edges" in s
        assert "density" in s

    def test_stats_density_positive(self):
        kg = XinAnKnowledgeGraph()
        s = kg.stats()
        assert s["density"] > 0

    def test_stats_density_range(self):
        kg = XinAnKnowledgeGraph()
        s = kg.stats()
        assert 0 < s["density"] <= 1

    def test_stats_nodes_edges_consistent(self):
        kg = XinAnKnowledgeGraph()
        s = kg.stats()
        assert s["nodes"] == kg.graph.number_of_nodes()
        assert s["edges"] == kg.graph.number_of_edges()
