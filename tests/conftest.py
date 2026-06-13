"""Pytest configuration and fixtures for XinAn-Med-GraphRAG tests."""
import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def knowledge_graph():
    """Create a shared knowledge graph instance for tests."""
    from backend.models.xinan_kg import XinAnKnowledgeGraph
    return XinAnKnowledgeGraph()


@pytest.fixture(scope="session")
def ner():
    """Create a shared NER instance for tests."""
    from backend.models.ancient_ner import AncientChineseNER
    return AncientChineseNER()


@pytest.fixture(scope="session")
def aligner():
    """Create a shared aligner instance for tests."""
    from backend.models.terminology_aligner import TerminologyAligner
    return TerminologyAligner()


@pytest.fixture(scope="session")
def engine():
    """Create a shared GraphRAG engine instance for tests."""
    from backend.models.graphrag_engine import GraphRAGEngine
    return GraphRAGEngine()
