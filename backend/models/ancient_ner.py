"""AncientChineseNER - regex+dictionary based NER for ancient TCM text."""
import re
from typing import List, Tuple


class AncientChineseNER:
    """Named Entity Recognition for ancient Traditional Chinese Medicine text.

    Entity types:
        person  - 医家 (medical masters)
        formula - 方剂 (formulas)
        herb    - 中药 (herbs/ingredients)
        syndrome- 证型 (syndromes)
        disease - 病名 (diseases)
        symptom - 症状 (symptoms)
        book    - 书名 (medical texts)
    """

    # ------------------------------------------------------------------ #
    #  Dictionaries
    # ------------------------------------------------------------------ #
    PERSONS = [
        "汪机", "孙一奎", "程国彭", "吴谦", "方广", "徐春甫", "汪昂", "吴澄",
        "叶桂", "程杏轩", "郑重光", "程衍道", "吴崑", "方有执", "罗美", "许豫和",
        "王仲奇", "王少峰", "程门雪", "叶熙春", "郑梅涧", "张仲景", "李东垣",
        "朱丹溪", "刘完素", "张从正", "王好古", "薛己", "张景岳", "李时珍",
        "扁鹊", "华佗", "孙思邈", "王叔和", "皇甫谧", "陶弘景", "葛洪",
        "巢元方", "钱乙", "陈自明", "严用和", "王纶", "赵献可", "缪希雍",
    ]

    FORMULAS = [
        "参苓白术散", "六味地黄丸", "补中益气汤", "归脾汤", "逍遥散", "四君子汤",
        "四物汤", "八珍汤", "十全大补汤", "天王补心丹", "安宫牛黄丸", "至宝丹",
        "紫雪丹", "苏合香丸", "保和丸", "二陈汤", "温胆汤", "龙胆泻肝汤",
        "白虎汤", "麻黄汤", "桂枝汤", "小柴胡汤", "真武汤", "五苓散",
        "半夏泻心汤", "止嗽散", "养阴清肺汤", "玉屏风散", "二仙汤", "固本培元方",
        "银翘散", "桑菊饮", "荆防败毒散", "藿香正气散", "三仁汤", "半夏白术天麻汤",
        "血府逐瘀汤", "桃红四物汤", "独活寄生汤", "川芎茶调散",
    ]

    HERBS = [
        "人参", "黄芪", "白术", "茯苓", "甘草", "当归", "川芎", "白芍",
        "熟地黄", "山茱萸", "山药", "泽泻", "牡丹皮", "柴胡", "陈皮", "升麻",
        "防风", "桔梗", "薄荷", "荆芥", "紫菀", "百部", "龙眼肉", "酸枣仁",
        "柏子仁", "薏苡仁", "莲子", "砂仁", "生地黄", "白前", "半夏", "黄连",
        "黄芩", "大黄", "附子", "干姜", "肉桂", "桂枝", "麻黄", "杏仁",
        "桃仁", "红花", "丹参", "三七", "天麻", "钩藤", "石决明", "龙骨",
        "牡蛎", "五味子", "麦冬", "天冬", "石斛", "枸杞子", "女贞子",
        "墨旱莲", "龟板", "鳖甲", "阿胶", "何首乌", "灵芝", "黄精",
    ]

    SYNDROMES = [
        "脾胃虚弱", "气血两虚", "肝郁脾虚", "阴虚火旺", "痰湿阻络", "肾阳虚",
        "肾阴虚", "肝阳上亢", "气滞血瘀", "痰热内扰", "心脾两虚", "肺脾气虚",
        "肝肾阴虚", "脾肾阳虚", "寒湿困脾", "湿热蕴脾", "心肾不交", "肝火上炎",
        "气阴两虚", "阴阳两虚", "营卫不和", "太阳病", "阳明病", "少阳病",
        "太阴病", "少阴病", "厥阴病", "卫分证", "气分证", "营分证", "血分证",
    ]

    DISEASES = [
        "消渴", "中风", "痹证", "眩晕", "不寐", "心悸", "咳嗽", "水肿",
        "黄疸", "泄泻", "噎膈", "积聚", "痿证", "厥证", "郁证", "癫狂",
        "痫证", "遗精", "阳痿", "虚劳", "肺痨", "吐血", "便血", "尿血",
        "鼻衄", "齿衄", "瘿瘤", "疝气", "淋证", "癃闭", "疟疾", "痢疾",
        "霍乱", "伤寒", "温病", "风温", "春温", "暑温", "秋燥", "冬温",
    ]

    SYMPTOMS = [
        "发热", "恶寒", "恶风", "自汗", "盗汗", "口渴", "口苦", "纳呆",
        "腹胀", "便溏", "便秘", "小便不利", "小便频数", "头痛", "头晕",
        "耳鸣", "目眩", "失眠", "多梦", "健忘", "乏力", "气短", "胸闷",
        "心烦", "胁痛", "腰痛", "膝软", "手足麻木", "口干", "咽干",
        "舌淡", "舌红", "苔白", "苔黄", "苔腻", "脉浮", "脉沉", "脉细",
        "脉弦", "脉滑", "脉数", "脉迟", "面色萎黄", "面色苍白", "面色潮红",
    ]

    BOOKS = [
        "石山医案", "赤水玄珠", "医旨绪余", "医学心悟", "医宗金鉴", "丹溪心法附余",
        "古今医统大全", "本草备要", "汤头歌诀", "不居集", "医述", "医方考",
        "伤寒论条辨", "古今名医方论", "幼科金针", "心印绀珠经", "王仲奇医案",
        "程门雪医案", "伤寒论", "金匮要略", "黄帝内经", "神农本草经",
        "难经", "温病条辨", "本草纲目", "千金要方", "外台秘要", "肘后备急方",
        "太平惠民和剂局方", "景岳全书", "类经", "素问", "灵枢",
    ]

    # Book title patterns: X经, X论, X方, X案, X录, etc.
    _BOOK_PATTERNS = re.compile(
        r'[\u4e00-\u9fff]{2,6}(?:经|论|方|案|录|集|考|鉴|要|诀|志|钞|略|全书|心法|条辨|金针|大成|大全|备要|绪余|玄珠)'
    )

    def __init__(self):
        # Build lookup dicts (longest-match first)
        self._dicts = {
            "person":   sorted(self.PERSONS, key=len, reverse=True),
            "formula":  sorted(self.FORMULAS, key=len, reverse=True),
            "herb":     sorted(self.HERBS, key=len, reverse=True),
            "syndrome": sorted(self.SYNDROMES, key=len, reverse=True),
            "disease":  sorted(self.DISEASES, key=len, reverse=True),
            "symptom":  sorted(self.SYMPTOMS, key=len, reverse=True),
            "book":     sorted(self.BOOKS, key=len, reverse=True),
        }

    # ------------------------------------------------------------------ #
    #  Core extraction
    # ------------------------------------------------------------------ #
    def extract_from_text(self, text: str) -> List[Tuple[str, str, int]]:
        """Extract entities from text.

        Returns:
            list of (entity_text, entity_type, start_position)
        """
        results: List[Tuple[str, str, int]] = []
        seen_spans: set = set()          # avoid overlapping matches

        # 1) Dictionary-based matching (greedy, longest first)
        for etype, vocab in self._dicts.items():
            for term in vocab:
                start = 0
                while True:
                    pos = text.find(term, start)
                    if pos == -1:
                        break
                    # check no overlap
                    span = (pos, pos + len(term))
                    if not any(s <= pos < e or s < span[1] <= e
                               for s, e in seen_spans):
                        results.append((term, etype, pos))
                        seen_spans.add(span)
                    start = pos + 1

        # 2) Regex pattern for book titles not already in dictionary
        for m in self._BOOK_PATTERNS.finditer(text):
            span = (m.start(), m.end())
            if not any(s <= m.start() < e or s < span[1] <= e
                       for s, e in seen_spans):
                results.append((m.group(), "book", m.start()))
                seen_spans.add(span)

        results.sort(key=lambda x: x[2])
        return results

    def extract_entities_only(self, text: str) -> List[str]:
        """Return deduplicated entity names only."""
        return list(dict.fromkeys(e for e, _, _ in self.extract_from_text(text)))

    def extract_by_type(self, text: str) -> dict:
        """Return {type: [entities]} grouped dict."""
        grouped: dict = {}
        for ent, etype, _ in self.extract_from_text(text):
            grouped.setdefault(etype, [])
            if ent not in grouped[etype]:
                grouped[etype].append(ent)
        return grouped
