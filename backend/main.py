"""新安医学古籍-现代病例GraphRAG知识平台"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="XinAn-Med-GraphRAG", version="0.2.0", description="新安医学古籍-现代病例GraphRAG知识平台")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Register routers
from backend.api.query import router as query_router
from backend.api.graph import router as graph_router
app.include_router(query_router)
app.include_router(graph_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "XinAn-Med-GraphRAG", "version": "0.2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8024)
