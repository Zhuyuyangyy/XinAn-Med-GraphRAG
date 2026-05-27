"""TerminologyAligner - map ancient TCM terms to modern equivalents."""
import re
from typing import List, Tuple


class TerminologyAligner:
    """Align ancient medical terminology with modern TCM / biomedical terms.

    Provides align_term() for single-term lookups and align_text() for
    batch replacement inside running text.
    """

    # 40+ ancient -> modern mapping pairs
    MAPPING = {
        # Disease / condition names
        "伤寒":     "外感病",
        "中风":     "卒中",
        "消渴":     "糖尿病",
        "痹证":     "风湿痹病",
        "不寐":     "失眠症",
        "心悸":     "心律失常",
        "眩晕":     "高血压相关眩晕",
        "噎膈":     "食管癌",
        "积聚":     "腹部肿块",
        "黄疸":     "黄疸(肝胆疾病)",
        "水肿":     "水肿(肾病综合征)",
        "泄泻":     "腹泻",
        "痢疾":     "细菌性痢疾",
        "疟疾":     "疟疾",
        "霍乱":     "霍乱/急性胃肠炎",
        "肺痨":     "肺结核",
        "虚劳":     "慢性消耗性疾病",
        "痿证":     "肌肉萎缩性疾病",
        "厥证":     "晕厥",
        "郁证":     "抑郁症/焦虑症",
        "癫狂":     "精神分裂症",
        "痫证":     "癫痫",
        "瘿瘤":     "甲状腺肿",
        "疝气":     "腹股沟疝",
        "淋证":     "泌尿系感染/结石",
        "癃闭":     "尿潴留",
        "遗精":     "遗精症",
        "阳痿":     "勃起功能障碍",
        "吐血":     "上消化道出血",
        "便血":     "下消化道出血",
        "尿血":     "血尿",
        "鼻衄":     "鼻出血",
        "齿衄":     "牙龈出血",
        "风温":     "流行性感冒",
        "春温":     "春季传染病",
        "暑温":     "中暑/夏季热病",
        "秋燥":     "秋季干燥症",
        # Syndrome / pattern names
        "太阳病":   "表证",
        "阳明病":   "里实热证",
        "少阳病":   "半表半里证",
        "太阴病":   "脾虚寒证",
        "少阴病":   "心肾阳虚证",
        "厥阴病":   "寒热错杂证",
        # Body / concept mapping
        "命门":     "肾阳/内分泌功能",
        "三焦":     "上中下三焦(体液代谢系统)",
        "卫气":     "免疫防御功能",
        "营气":     "营养代谢功能",
        "元气":     "先天免疫/体质基础",
        "膏粱":     "高脂饮食",
        "膏肓":     "病入膏肓(晚期疾病)",
        # Ancient herb names -> modern names
        "术":       "白术",
        "芍药":     "白芍",
        "地黄":     "熟地黄",
        "桂":       "桂枝/肉桂",
        "附子":     "附子(黑顺片)",
        "半夏":     "半夏(法半夏)",
    }

    def __init__(self, extra_mappings: dict | None = None):
        """Init with optional additional mappings.

        Args:
            extra_mappings: dict of {ancient_term: modern_term}
        """
        self.mapping = dict(self.MAPPING)
        if extra_mappings:
            self.mapping.update(extra_mappings)
        # Sort by length (longest first) for greedy matching
        self._sorted_keys = sorted(self.mapping.keys(), key=len, reverse=True)

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def align_term(self, ancient_term: str) -> str | None:
        """Look up a single ancient term.

        Returns:
            Modern equivalent if found, else None.
        """
        return self.mapping.get(ancient_term)

    def align_text(self, text: str) -> str:
        """Replace all known ancient terms in *text* with their modern equivalents.

        Preserves the original term in parentheses for reference:
            "消渴" -> "消渴(糖尿病)"
        """
        result = text
        for ancient in self._sorted_keys:
            modern = self.mapping[ancient]
            if ancient in result and ancient != modern:
                result = result.replace(ancient, f"{ancient}({modern})")
        return result

    def align_text_strict(self, text: str) -> str:
        """Replace ancient terms without preserving originals.

            "消渴" -> "糖尿病"
        """
        result = text
        for ancient in self._sorted_keys:
            modern = self.mapping[ancient]
            if ancient in result:
                result = result.replace(ancient, modern)
        return result

    def find_ancient_terms(self, text: str) -> List[Tuple[str, str, int]]:
        """Find all ancient terms present in text.

        Returns:
            list of (ancient_term, modern_term, position)
        """
        results = []
        seen_spans = set()
        for ancient in self._sorted_keys:
            start = 0
            while True:
                pos = text.find(ancient, start)
                if pos == -1:
                    break
                span = (pos, pos + len(ancient))
                if not any(s <= pos < e or s < span[1] <= e
                           for s, e in seen_spans):
                    results.append((ancient, self.mapping[ancient], pos))
                    seen_spans.add(span)
                start = pos + 1
        results.sort(key=lambda x: x[2])
        return results

    def get_all_mappings(self) -> dict:
        """Return the full mapping dict."""
        return dict(self.mapping)
