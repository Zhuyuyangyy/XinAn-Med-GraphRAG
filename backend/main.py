"""新安医学古籍-现代病例GraphRAG知识平台"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="XinAn-Med-GraphRAG", version="0.1.0", description="新安医学古籍-现代病例GraphRAG知识平台")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "XinAn-Med-GraphRAG", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8024)
