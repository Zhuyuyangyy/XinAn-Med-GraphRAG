"""POST /api/query - GraphRAG query endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["query"])

# Lazy singleton engine
_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        from backend.models.graphrag_engine import GraphRAGEngine
        _engine = GraphRAGEngine()
    return _engine


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: Optional[int] = Field(8, ge=1, le=50, description="返回结果数量")


class QueryResponse(BaseModel):
    question: str
    answer: str
    context_triples: list
    triple_count: int


@router.post("/query", response_model=QueryResponse, summary="GraphRAG问答")
async def query_endpoint(req: QueryRequest):
    """Retrieve relevant knowledge graph triples and generate an answer."""
    engine = _get_engine()
    result = engine.query(req.question, top_k=req.top_k)
    return QueryResponse(**result)
