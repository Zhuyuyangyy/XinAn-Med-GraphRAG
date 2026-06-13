"""Comprehensive tests for AncientChineseNER module."""
import pytest
from backend.models.ancient_ner import AncientChineseNER


class TestAncientChineseNERInit:
    """Test NER initialization."""

    def test_init_creates_dicts(self):
        ner = AncientChineseNER()
        assert hasattr(ner, '_dicts')
        assert len(ner._dicts) == 7

    def test_init_has_all_entity_types(self):
        ner = AncientChineseNER()
        expected_types = ["person", "formula", "herb", "syndrome", "disease", "symptom", "book"]
        for etype in expected_types:
            assert etype in ner._dicts

    def test_init_dictionaries_sorted_by_length(self):
        ner = AncientChineseNER()
        for etype, vocab in ner._dicts.items():
            for i in range(len(vocab) - 1):
                assert len(vocab[i]) >= len(vocab[i+1]), \
                    f"{etype} dictionary not sorted by length"


class TestExtractFromText:
    """Test entity extraction from text."""

    def test_extract_person(self):
        ner = AncientChineseNER()
        text = "汪机是明代著名医家"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("汪机", "person") in entities

    def test_extract_formula(self):
        ner = AncientChineseNER()
        text = "参苓白术散是经典方剂"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("参苓白术散", "formula") in entities

    def test_extract_herb(self):
        ner = AncientChineseNER()
        text = "人参大补元气"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("人参", "herb") in entities

    def test_extract_syndrome(self):
        ner = AncientChineseNER()
        text = "患者脾胃虚弱"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("脾胃虚弱", "syndrome") in entities

    def test_extract_disease(self):
        ner = AncientChineseNER()
        text = "消渴病的治疗"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("消渴", "disease") in entities

    def test_extract_symptom(self):
        ner = AncientChineseNER()
        text = "患者发热恶寒"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("发热", "symptom") in entities

    def test_extract_book(self):
        ner = AncientChineseNER()
        text = "石山医案记载详实"
        results = ner.extract_from_text(text)
        entities = [(e, t) for e, t, _ in results]
        assert ("石山医案", "book") in entities

    def test_extract_multiple_entities(self):
        ner = AncientChineseNER()
        text = "汪机善用参苓白术散治疗脾胃虚弱"
        results = ner.extract_from_text(text)
        entities = [e for e, _, _ in results]
        assert "汪机" in entities
        assert "参苓白术散" in entities
        assert "脾胃虚弱" in entities

    def test_extract_no_overlap(self):
        ner = AncientChineseNER()
        text = "参苓白术散中的人参"
        results = ner.extract_from_text(text)
        positions = [(pos, pos + len(e)) for e, _, pos in results]
        for i, (s1, e1) in enumerate(positions):
            for j, (s2, e2) in enumerate(positions):
                if i != j:
                    assert not (s1 <= s2 < e1 or s1 < e2 <= e1), \
                        "Overlapping entities detected"

    def test_extract_empty_text(self):
        ner = AncientChineseNER()
        results = ner.extract_from_text("")
        assert results == []

    def test_extract_no_entities(self):
        ner = AncientChineseNER()
        text = "这是一段普通文本"
        results = ner.extract_from_text(text)
        assert len(results) == 0

    def test_extract_positions_sorted(self):
        ner = AncientChineseNER()
        text = "汪机善用参苓白术散治疗脾胃虚弱"
        results = ner.extract_from_text(text)
        positions = [pos for _, _, pos in results]
        assert positions == sorted(positions)

    def test_extract_regex_book_pattern(self):
        ner = AncientChineseNER()
        text = "参考黄帝内经和素问"
        results = ner.extract_from_text(text)
        entities = [e for e, _, _ in results]
        assert "黄帝内经" in entities


class TestExtractEntitiesOnly:
    """Test entity-only extraction."""

    def test_extract_entities_only_returns_list(self):
        ner = AncientChineseNER()
        text = "汪机善用参苓白术散"
        result = ner.extract_entities_only(text)
        assert isinstance(result, list)

    def test_extract_entities_only_no_duplicates(self):
        ner = AncientChineseNER()
        text = "汪机汪机汪机"
        result = ner.extract_entities_only(text)
        assert len(result) == 1

    def test_extract_entities_only_returns_names(self):
        ner = AncientChineseNER()
        text = "汪机善用参苓白术散治疗脾胃虚弱"
        result = ner.extract_entities_only(text)
        assert "汪机" in result
        assert "参苓白术散" in result


class TestExtractByType:
    """Test extraction grouped by type."""

    def test_extract_by_type_returns_dict(self):
        ner = AncientChineseNER()
        text = "汪机善用参苓白术散"
        result = ner.extract_by_type(text)
        assert isinstance(result, dict)

    def test_extract_by_type_groups_correctly(self):
        ner = AncientChineseNER()
        text = "汪机善用参苓白术散治疗脾胃虚弱"
        result = ner.extract_by_type(text)
        assert "person" in result
        assert "汪机" in result["person"]
        assert "formula" in result
        assert "参苓白术散" in result["formula"]
        assert "syndrome" in result
        assert "脾胃虚弱" in result["syndrome"]

    def test_extract_by_type_empty_text(self):
        ner = AncientChineseNER()
        result = ner.extract_by_type("")
        assert result == {}

    def test_extract_by_type_no_duplicates_in_group(self):
        ner = AncientChineseNER()
        text = "汪机和汪机都是名医"
        result = ner.extract_by_type(text)
        assert len(result["person"]) == 1
