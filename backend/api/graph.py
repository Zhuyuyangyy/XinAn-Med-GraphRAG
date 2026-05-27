"""GET /api/graph/stats and /api/graph/search - Graph endpoints."""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/graph", tags=["graph"])

_kg = None

def _get_kg():
    global _kg
    if _kg is None:
        from backend.models.xinan_kg import XinAnKnowledgeGraph
        _kg = XinAnKnowledgeGraph()
    return _kg


@router.get("/stats", summary="知识图谱统计")
async def graph_stats():
    """Return knowledge graph statistics (node/edge count, density)."""
    kg = _get_kg()
    return kg.stats()


@router.get("/search", summary="知识图谱搜索")
async def graph_search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="最大返回数"),
):
    """Search graph entities by keyword and return matching triples."""
    kg = _get_kg()
    matched_nodes = kg.search(q)[:limit]
    results = []
    for node in matched_nodes:
        neighbors = kg.get_neighbors(node)
        results.append({"entity": node, "outgoing": neighbors["outgoing"], "incoming": neighbors["incoming"]})
    return {"query": q, "match_count": len(results), "matches": results}
