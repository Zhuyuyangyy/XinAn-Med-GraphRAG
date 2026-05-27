# XinAn-Med-GraphRAG

新安医学古籍-现代病例 GraphRAG 知识平台

## 核心创新点

1. **新安医学传承** — 徽州新安医学古籍数字化与知识抽取
2. **GraphRAG** — 基于知识图谱的检索增强生成
3. **古今关联** — 古籍方剂与现代临床病例的关联分析
4. **辨证推理** — 基于图结构的中医辨证论治推理

## 快速开始

```bash
pip install -e .
uvicorn backend.main:app --port 8024 --reload
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/query/ask` | POST | 知识问答 |
| `/api/graph/entities` | GET | 实体查询 |
| `/api/graph/relations` | GET | 关系查询 |

## License

MIT
