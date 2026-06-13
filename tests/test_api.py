"""Comprehensive tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data

    def test_health_status_ok(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_service_name(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "XinAn-Med-GraphRAG"


class TestQueryEndpoint:
    """Test GraphRAG query endpoint."""

    def test_query_returns_200(self, client):
        response = client.post("/api/query", json={"question": "汪机"})
        assert response.status_code == 200

    def test_query_returns_json(self, client):
        response = client.post("/api/query", json={"question": "汪机"})
        data = response.json()
        assert "question" in data
        assert "answer" in data
        assert "context_triples" in data
        assert "triple_count" in data

    def test_query_preserves_question(self, client):
        response = client.post("/api/query", json={"question": "汪机擅长什么？"})
        data = response.json()
        assert data["question"] == "汪机擅长什么？"

    def test_query_with_top_k(self, client):
        response = client.post("/api/query", json={"question": "汪机", "top_k": 5})
        assert response.status_code == 200

    def test_query_ancient_terms(self, client):
        response = client.post("/api/query", json={"question": "消渴病的治疗"})
        data = response.json()
        assert data["triple_count"] > 0

    def test_query_formula(self, client):
        response = client.post("/api/query", json={"question": "参苓白术散的组成"})
        data = response.json()
        assert data["triple_count"] > 0

    def test_query_empty_question_fails(self, client):
        response = client.post("/api/query", json={"question": ""})
        assert response.status_code == 422

    def test_query_missing_question_fails(self, client):
        response = client.post("/api/query", json={})
        assert response.status_code == 422

    def test_query_invalid_top_k_fails(self, client):
        response = client.post("/api/query", json={"question": "汪机", "top_k": 0})
        assert response.status_code == 422

    def test_query_top_k_too_large_fails(self, client):
        response = client.post("/api/query", json={"question": "汪机", "top_k": 100})
        assert response.status_code == 422


class TestGraphStatsEndpoint:
    """Test graph statistics endpoint."""

    def test_stats_returns_200(self, client):
        response = client.get("/api/graph/stats")
        assert response.status_code == 200

    def test_stats_returns_json(self, client):
        response = client.get("/api/graph/stats")
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "density" in data

    def test_stats_has_data(self, client):
        response = client.get("/api/graph/stats")
        data = response.json()
        assert data["nodes"] >= 100
        assert data["edges"] >= 150

    def test_stats_density_positive(self, client):
        response = client.get("/api/graph/stats")
        data = response.json()
        assert data["density"] > 0


class TestGraphSearchEndpoint:
    """Test graph search endpoint."""

    def test_search_returns_200(self, client):
        response = client.get("/api/graph/search", params={"q": "汪机"})
        assert response.status_code == 200

    def test_search_returns_json(self, client):
        response = client.get("/api/graph/search", params={"q": "汪机"})
        data = response.json()
        assert "query" in data
        assert "match_count" in data
        assert "matches" in data

    def test_search_finds_entities(self, client):
        response = client.get("/api/graph/search", params={"q": "汪机"})
        data = response.json()
        assert data["match_count"] >= 1

    def test_search_match_structure(self, client):
        response = client.get("/api/graph/search", params={"q": "汪机"})
        data = response.json()
        for match in data["matches"]:
            assert "entity" in match
            assert "outgoing" in match
            assert "incoming" in match

    def test_search_with_limit(self, client):
        response = client.get("/api/graph/search", params={"q": "医", "limit": 5})
        data = response.json()
        assert data["match_count"] <= 5

    def test_search_no_results(self, client):
        response = client.get("/api/graph/search", params={"q": "ZZZZNOTFOUND"})
        data = response.json()
        assert data["match_count"] == 0

    def test_search_missing_query_fails(self, client):
        response = client.get("/api/graph/search")
        assert response.status_code == 422

    def test_search_empty_query_fails(self, client):
        response = client.get("/api/graph/search", params={"q": ""})
        assert response.status_code == 422

    def test_search_formula(self, client):
        response = client.get("/api/graph/search", params={"q": "参苓白术散"})
        data = response.json()
        assert data["match_count"] >= 1

    def test_search_herb(self, client):
        response = client.get("/api/graph/search", params={"q": "人参"})
        data = response.json()
        assert data["match_count"] >= 1
