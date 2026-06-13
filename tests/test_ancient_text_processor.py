"""Comprehensive tests for AncientTextProcessor module."""
import pytest
from backend.models.ancient_text_processor import AncientTextProcessor


class TestAncientTextProcessorNormalize:
    """Test text normalization."""

    def test_normalize_removes_spaces(self):
        processor = AncientTextProcessor()
        result = processor.normalize("汪 机 是 名 医")
        assert " " not in result

    def test_normalize_removes_tabs(self):
        processor = AncientTextProcessor()
        result = processor.normalize("汪机\t是\t名医")
        assert "\t" not in result

    def test_normalize_removes_newlines(self):
        processor = AncientTextProcessor()
        result = processor.normalize("汪机\n是\n名医")
        assert "\n" not in result

    def test_normalize_preserves_chinese(self):
        processor = AncientTextProcessor()
        result = processor.normalize("汪机是名医")
        assert result == "汪机是名医"

    def test_normalize_empty_string(self):
        processor = AncientTextProcessor()
        result = processor.normalize("")
        assert result == ""

    def test_normalize_only_spaces(self):
        processor = AncientTextProcessor()
        result = processor.normalize("   ")
        assert result == ""


class TestAncientTextProcessorExtractFormulas:
    """Test formula extraction."""

    def test_extract_formula_with_tang(self):
        processor = AncientTextProcessor()
        result = processor.extract_formulas("补中益气汤是经典方剂")
        assert "补中益气汤" in result

    def test_extract_formula_with_san(self):
        processor = AncientTextProcessor()
        result = processor.extract_formulas("参苓白术散是经典方剂")
        assert "参苓白术散" in result

    def test_extract_multiple_formulas(self):
        processor = AncientTextProcessor()
        result = processor.extract_formulas("补中益气汤和参苓白术散都是经典方剂")
        assert len(result) >= 2

    def test_extract_no_formulas(self):
        processor = AncientTextProcessor()
        result = processor.extract_formulas("这是普通文本")
        assert result == []

    def test_extract_empty_string(self):
        processor = AncientTextProcessor()
        result = processor.extract_formulas("")
        assert result == []
