"""Ancient TCM text processing."""
import re

class AncientTextProcessor:
    def normalize(self, text): return re.sub(r"\s+", "", text)
    def extract_formulas(self, text): return re.findall(r"[一-鿿]+汤|[一-鿿]+散", text)
