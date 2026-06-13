"""Comprehensive tests for GraphRAGEngine and BM25Index modules."""
import pytest
from backend.models.graphrag_engine import BM25Index, GraphRAGEngine


class TestBM25IndexInit:
    """Test BM25 index initialization."""

    def test_init_default_params(self):
        bm25 = BM25Index()
        assert bm25.k1 == 1.5
        assert bm25.b == 0.75
        assert bm25.N == 0

    def test_init_custom_params(self):
        bm25 = BM25Index(k1=2.0, b=0.5)
        assert bm25.k1 == 2.0
        assert bm25.b == 0.5

    def test_init_empty_docs(self):
        bm25 = BM25Index()
        assert bm25.docs == []
        assert bm25.doc_ids == []
        assert bm25.doc_len == []


class TestBM25Tokenize:
    """Test BM25 tokenization."""

    def test_tokenize_chinese(self):
        tokens = BM25Index._tokenize("汪机是名医")
        assert "汪" in tokens
        assert "机" in tokens

    def test_tokenize_english(self):
        tokens = BM25Index._tokenize("Hello World")
        assert "hello" in tokens
        assert "world" in tokens

    def test_tokenize_mixed(self):
        tokens = BM25Index._tokenize("Python编程")
        assert "python" in tokens
        assert "编" in tokens

    def test_tokenize_empty(self):
        tokens = BM25Index._tokenize("")
        assert tokens == []

    def test_tokenize_numbers(self):
        tokens = BM25Index._tokenize("123")
        assert "123" in tokens


class TestBM25Add:
    """Test adding documents to BM25 index."""

    def test_add_single_doc(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        assert bm25.N == 1
        assert len(bm25.docs) == 1

    def test_add_multiple_docs(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        bm25.add("doc2", "参苓白术散")
        assert bm25.N == 2
        assert len(bm25.docs) == 2

    def test_add_updates_avg_dl(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机")
        bm25.add("doc2", "参苓白术散是经典方剂")
        assert bm25.avg_dl > 0

    def test_add_updates_df(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        bm25.add("doc2", "汪机善用参苓白术散")
        # 汪 appears in both docs
        assert bm25.df.get("汪", 0) == 2


class TestBM25Score:
    """Test BM25 scoring."""

    def test_score_empty_index(self):
        bm25 = BM25Index()
        result = bm25.score("汪机")
        assert result == []

    def test_score_returns_list(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        result = bm25.score("汪机")
        assert isinstance(result, list)

    def test_score_returns_tuples(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        result = bm25.score("汪机")
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_score_sorted_by_relevance(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        bm25.add("doc2", "参苓白术散是经典方剂")
        result = bm25.score("汪机")
        if len(result) >= 2:
            assert result[0][1] >= result[1][1]

    def test_score_top_k(self):
        bm25 = BM25Index()
        for i in range(20):
            bm25.add(f"doc{i}", f"文档{i}")
        result = bm25.score("文档", top_k=5)
        assert len(result) <= 5

    def test_score_no_match(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机是名医")
        result = bm25.score("ZZZZNOTFOUND")
        assert result == []

    def test_score_chinese_query(self):
        bm25 = BM25Index()
        bm25.add("doc1", "汪机 善用 参苓白术散")
        result = bm25.score("参苓白术散")
        assert len(result) > 0


class TestGraphRAGEngineInit:
    """Test GraphRAG engine initialization."""

    def test_init_creates_kg(self):
        engine = GraphRAGEngine()
        assert engine.kg is not None

    def test_init_creates_bm25(self):
        engine = GraphRAGEngine()
        assert engine.bm25 is not None

    def test_init_creates_ner(self):
        engine = GraphRAGEngine()
        assert engine.ner is not None

    def test_init_creates_aligner(self):
        engine = GraphRAGEngine()
        assert engine.aligner is not None

    def test_init_builds_index(self):
        engine = GraphRAGEngine()
        assert engine.bm25.N > 0

    def test_init_with_custom_kg(self):
        from backend.models.xinan_kg import XinAnKnowledgeGraph
        kg = XinAnKnowledgeGraph()
        engine = GraphRAGEngine(kg=kg)
        assert engine.kg is kg


class TestGraphRAGRetrieve:
    """Test retrieval functionality."""

    def test_retrieve_returns_list(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("汪机")
        assert isinstance(result, list)

    def test_retrieve_returns_dicts(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("汪机")
        for item in result:
            assert isinstance(item, dict)

    def test_retrieve_dict_structure(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("汪机")
        for item in result:
            assert "subject" in item
            assert "relation" in item
            assert "object" in item
            assert "score" in item

    def test_retrieve_with_ner_expansion(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("汪机擅长治疗脾胃虚弱")
        assert len(result) > 0

    def test_retrieve_with_terminology_alignment(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("消渴病的治疗")
        assert len(result) > 0

    def test_retrieve_top_k(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("新安医学", top_k=3)
        # Should return limited results
        assert len(result) <= 3 * 3  # top_k * 3 is the limit

    def test_retrieve_empty_query(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("")
        assert isinstance(result, list)

    def test_retrieve_deduplication(self):
        engine = GraphRAGEngine()
        result = engine.retrieve("汪机")
        keys = [f"{t['subject']}|{t['relation']}|{t['object']}" for t in result]
        assert len(keys) == len(set(keys))


class TestGraphRAGGenerate:
    """Test answer generation."""

    def test_generate_returns_string(self):
        engine = GraphRAGEngine()
        triples = [{"subject": "汪机", "relation": "代表医家", "object": "新安医学", "score": 1.0}]
        result = engine.generate("汪机", triples)
        assert isinstance(result, str)

    def test_generate_with_triples(self):
        engine = GraphRAGEngine()
        triples = [
            {"subject": "汪机", "relation": "代表医家", "object": "新安医学", "score": 1.0},
            {"subject": "汪机", "relation": "著作", "object": "石山医案", "score": 0.8},
        ]
        result = engine.generate("汪机", triples)
        assert "汪机" in result
        assert "新安医学" in result

    def test_generate_empty_triples(self):
        engine = GraphRAGEngine()
        result = engine.generate("测试问题", [])
        assert "未找到" in result

    def test_generate_limits_triples(self):
        engine = GraphRAGEngine()
        triples = [
            {"subject": f"实体{i}", "relation": "关系", "object": f"目标{i}", "score": 1.0}
            for i in range(20)
        ]
        result = engine.generate("测试", triples)
        # Should only show top 10
        assert result.count("实体") <= 10


class TestGraphRAGQuery:
    """Test full RAG query pipeline."""

    def test_query_returns_dict(self):
        engine = GraphRAGEngine()
        result = engine.query("汪机")
        assert isinstance(result, dict)

    def test_query_has_required_keys(self):
        engine = GraphRAGEngine()
        result = engine.query("汪机")
        assert "question" in result
        assert "answer" in result
        assert "context_triples" in result
        assert "triple_count" in result

    def test_query_preserves_question(self):
        engine = GraphRAGEngine()
        result = engine.query("汪机擅长什么？")
        assert result["question"] == "汪机擅长什么？"

    def test_query_with_ancient_terms(self):
        engine = GraphRAGEngine()
        result = engine.query("消渴病的治疗")
        assert result["triple_count"] > 0

    def test_query_with_modern_terms(self):
        engine = GraphRAGEngine()
        result = engine.query("参苓白术散的组成")
        assert result["triple_count"] > 0

    def test_query_triple_count_matches(self):
        engine = GraphRAGEngine()
        result = engine.query("汪机")
        assert result["triple_count"] == len(result["context_triples"])

    def test_query_empty_question(self):
        engine = GraphRAGEngine()
        result = engine.query("")
        assert isinstance(result, dict)

    def test_query_complex_question(self):
        engine = GraphRAGEngine()
        result = engine.query("汪机的固本培元学说中常用哪些方剂？")
        assert result["triple_count"] > 0
