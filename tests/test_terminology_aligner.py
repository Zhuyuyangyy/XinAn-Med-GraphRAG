"""Comprehensive tests for TerminologyAligner module."""
import pytest
from backend.models.terminology_aligner import TerminologyAligner


class TestTerminologyAlignerInit:
    """Test aligner initialization."""

    def test_init_creates_mapping(self):
        aligner = TerminologyAligner()
        assert hasattr(aligner, 'mapping')
        assert len(aligner.mapping) >= 40

    def test_init_sorted_keys(self):
        aligner = TerminologyAligner()
        for i in range(len(aligner._sorted_keys) - 1):
            assert len(aligner._sorted_keys[i]) >= len(aligner._sorted_keys[i+1])

    def test_init_with_extra_mappings(self):
        extra = {"测试古词": "测试现代词"}
        aligner = TerminologyAligner(extra_mappings=extra)
        assert aligner.align_term("测试古词") == "测试现代词"

    def test_init_extra_mappings_override(self):
        extra = {"消渴": "糖尿病(测试)"}
        aligner = TerminologyAligner(extra_mappings=extra)
        assert aligner.align_term("消渴") == "糖尿病(测试)"


class TestAlignTerm:
    """Test single term alignment."""

    def test_align_term_disease(self):
        aligner = TerminologyAligner()
        assert aligner.align_term("消渴") == "糖尿病"
        assert aligner.align_term("中风") == "卒中"
        assert aligner.align_term("伤寒") == "外感病"

    def test_align_term_syndrome(self):
        aligner = TerminologyAligner()
        assert aligner.align_term("太阳病") == "表证"
        assert aligner.align_term("阳明病") == "里实热证"

    def test_align_term_concept(self):
        aligner = TerminologyAligner()
        assert aligner.align_term("命门") == "肾阳/内分泌功能"
        assert aligner.align_term("三焦") == "上中下三焦(体液代谢系统)"

    def test_align_term_herb(self):
        aligner = TerminologyAligner()
        assert aligner.align_term("术") == "白术"
        assert aligner.align_term("芍药") == "白芍"

    def test_align_term_not_found(self):
        aligner = TerminologyAligner()
        assert aligner.align_term("不存在的词") is None

    def test_align_term_empty_string(self):
        aligner = TerminologyAligner()
        assert aligner.align_term("") is None


class TestAlignText:
    """Test text alignment with preserved originals."""

    def test_align_text_preserves_original(self):
        aligner = TerminologyAligner()
        text = "消渴病"
        result = aligner.align_text(text)
        assert "消渴" in result
        assert "糖尿病" in result

    def test_align_text_multiple_terms(self):
        aligner = TerminologyAligner()
        text = "此患者消渴日久，兼有中风之证"
        result = aligner.align_text(text)
        assert "糖尿病" in result
        assert "卒中" in result

    def test_align_text_no_match(self):
        aligner = TerminologyAligner()
        text = "这是一段普通文本"
        result = aligner.align_text(text)
        assert result == text

    def test_align_text_empty_string(self):
        aligner = TerminologyAligner()
        result = aligner.align_text("")
        assert result == ""

    def test_align_text_format(self):
        aligner = TerminologyAligner()
        text = "消渴"
        result = aligner.align_text(text)
        assert "(" in result
        assert ")" in result


class TestAlignTextStrict:
    """Test strict text alignment without preserved originals."""

    def test_align_text_strict_replaces(self):
        aligner = TerminologyAligner()
        text = "消渴病"
        result = aligner.align_text_strict(text)
        assert "消渴" not in result
        assert "糖尿病" in result

    def test_align_text_strict_multiple(self):
        aligner = TerminologyAligner()
        text = "此患者消渴日久，兼有中风之证"
        result = aligner.align_text_strict(text)
        assert "消渴" not in result
        assert "中风" not in result
        assert "糖尿病" in result
        assert "卒中" in result

    def test_align_text_strict_no_match(self):
        aligner = TerminologyAligner()
        text = "普通文本"
        result = aligner.align_text_strict(text)
        assert result == text


class TestFindAncientTerms:
    """Test finding ancient terms in text."""

    def test_find_ancient_terms_returns_list(self):
        aligner = TerminologyAligner()
        text = "消渴病"
        result = aligner.find_ancient_terms(text)
        assert isinstance(result, list)

    def test_find_ancient_terms_tuple_structure(self):
        aligner = TerminologyAligner()
        text = "消渴病"
        result = aligner.find_ancient_terms(text)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3

    def test_find_ancient_terms_multiple(self):
        aligner = TerminologyAligner()
        text = "此患者消渴日久，兼有中风之证"
        result = aligner.find_ancient_terms(text)
        assert len(result) >= 2
        terms = [term for term, _, _ in result]
        assert "消渴" in terms
        assert "中风" in terms

    def test_find_ancient_terms_sorted_by_position(self):
        aligner = TerminologyAligner()
        text = "中风兼消渴"
        result = aligner.find_ancient_terms(text)
        positions = [pos for _, _, pos in result]
        assert positions == sorted(positions)

    def test_find_ancient_terms_no_match(self):
        aligner = TerminologyAligner()
        text = "普通文本"
        result = aligner.find_ancient_terms(text)
        assert len(result) == 0


class TestGetAllMappings:
    """Test getting all mappings."""

    def test_get_all_mappings_returns_dict(self):
        aligner = TerminologyAligner()
        result = aligner.get_all_mappings()
        assert isinstance(result, dict)

    def test_get_all_mappings_has_data(self):
        aligner = TerminologyAligner()
        result = aligner.get_all_mappings()
        assert len(result) >= 40

    def test_get_all_mappings_contains_diseases(self):
        aligner = TerminologyAligner()
        result = aligner.get_all_mappings()
        assert "消渴" in result
        assert "中风" in result

    def test_get_all_mappings_returns_copy(self):
        aligner = TerminologyAligner()
        result1 = aligner.get_all_mappings()
        result1["测试"] = "测试"
        result2 = aligner.get_all_mappings()
        assert "测试" not in result2
