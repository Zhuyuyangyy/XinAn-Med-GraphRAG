<p align="center">
  <h1 align="center">XinAn-Med-GraphRAG</h1>
  <p align="center">
    <strong>XinAn Medical Knowledge Graph RAG System</strong>
  </p>
  <p align="center">
    Bridging ancient XinAn medical texts with modern clinical knowledge through Graph-based Retrieval-Augmented Generation
  </p>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#api-reference">API</a> &bull;
  <a href="#project-structure">Structure</a> &bull;
  <a href="#roadmap">Roadmap</a>
</p>

---

## Important Disclaimers

> **Naming Clarification:** The term "GraphRAG" in this project name is used loosely. The retrieval engine is a **BM25 keyword search** over a **manually curated knowledge graph**, not a learned or vector-based GraphRAG system (e.g., as described by Microsoft's GraphRAG). There is no graph neural network, no vector embedding retrieval, and no LLM-based graph reasoning in the current implementation. The name is retained for project branding only.
>
> **Knowledge Graph Origin:** The knowledge graph is **hand-authored as Python tuples** in `backend/models/xinan_kg.py`. It is not extracted from text by NLP/OCR pipelines. All 120+ nodes and 200+ edges were manually typed based on domain knowledge of XinAn Traditional Chinese Medicine. The NER and terminology alignment modules operate at query time only and do not populate the graph.
>
> **No External Evaluation:** Benchmarks, accuracy claims, and test coverage numbers in this repository have not been validated by external peer review. Self-assessments (including the OPTIMIZATION_REPORT) reflect the developers' own estimates.

## Overview

**XinAn-Med-GraphRAG** is a BM25-keyword-search-based retrieval system over a manually curated knowledge graph for XinAn Traditional Chinese Medicine (TCM). XinAn medicine is a prestigious regional TCM school originating from the Huizhou (Huizhou She) area of Anhui Province, with a lineage spanning over 600 years and contributions from more than 20 renowned medical masters.

The system digitizes and connects XinAn medical knowledge across three layers:

- **Ancient Text Understanding** -- Named Entity Recognition (NER) for classical Chinese medical texts, extracting medical masters, formulas, herbs, syndromes, diseases, and book references
- **Knowledge Graph Construction** -- A 120+ node directed knowledge graph (hand-authored as Python tuples) encoding relationships between XinAn medical masters, their formulas, academic schools, herb ingredients, and disease indications
- **BM25 Retrieval Pipeline** -- A BM25 keyword retrieval engine with graph traversal expansion and ancient-to-modern terminology alignment, enabling natural language queries over the XinAn medical knowledge base

## Key Features

- **XinAn Knowledge Graph** -- 120+ nodes and 200+ edges (manually authored tuples) covering 20 medical masters, 30 classic formulas, 60+ herbs, 20 syndromes, 15 academic schools, and 20 classical texts
- **Ancient Chinese Medical NER** -- Dictionary + regex-based entity recognition supporting 7 entity types: person, formula, herb, syndrome, disease, symptom, book
- **Terminology Alignment** -- 40+ ancient-to-modern term mappings (e.g., "consumptive thirst" to "diabetes mellitus", "wind-strike" to "stroke")
- **BM25 Retrieval Engine** -- Lightweight BM25 scorer optimized for CJK medical text with single-character tokenization
- **Multi-Hop Graph Traversal** -- 1-2 hop neighbor expansion for enriched context retrieval
- **NER-Aware Query Expansion** -- Automatic entity detection and terminology alignment in user queries
- **Template-Based Generation** -- Structured answer synthesis from retrieved knowledge triples (no LLM dependency required)
- **RESTful API** -- FastAPI-powered endpoints for knowledge graph queries, entity search, and RAG-based question answering
- **CI/CD Pipeline** -- GitHub Actions with Ruff linting and Pytest testing
- **Docker Support** -- Containerized deployment with Docker Compose for reproducible environments

## Architecture

```
                       +---------------------------+
                       |      User Question        |
                       |  (Ancient/Modern Chinese)  |
                       +------------+--------------+
                                    |
                                    v
                       +------------+--------------+
                       |   Terminology Alignment    |
                       |   Ancient -> Modern Terms   |
                       +------------+--------------+
                                    |
                                    v
                       +------------+--------------+
                       |   AncientChineseNER        |
                       |   Entity Detection (7 types)|
                       +------------+--------------+
                                    |
                                    v
                       +------------+--------------+
                       |   BM25 + Graph Retrieval   |
                       |   Query Expansion          |
                       |   1-2 Hop Graph Traversal  |
                       +------------+--------------+
                                    |
                       +------------+--------------+
                       |   XinAn Knowledge Graph    |
                       |   120+ Nodes | 200+ Edges |
                       |   NetworkX DiGraph         |
                       +------------+--------------+
                                    |
                                    v
                       +------------+--------------+
                       |   Answer Generation        |
                       |   Template-Based Synthesis  |
                       +------------+--------------+
                                    |
                                    v
                       +------------+--------------+
                       |   FastAPI Response          |
                       |   (port 8024)               |
                       +----------------------------+
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Runtime** | Python 3.10+ | Core language |
| **Web Framework** | FastAPI + Uvicorn | Async REST API server |
| **Knowledge Graph** | NetworkX | Directed graph storage and traversal |
| **Text Retrieval** | Custom BM25 | Keyword-based document retrieval |
| **NER** | Regex + Dictionary | Ancient Chinese medical entity recognition |
| **Machine Learning** | *(Not currently used)* | Reserved for future graph embedding / NER models |
| **Data Processing** | NumPy, Pandas | Data manipulation (used lightly; can be removed) |
| **Data Validation** | Pydantic v2 | Request/response schemas |
| **Configuration** | PyYAML, pydantic-settings | Data source configuration |
| **CI/CD** | GitHub Actions | Lint + test automation |
| **Linting** | Ruff | Code quality enforcement |
| **Containerization** | Docker + Docker Compose | Reproducible deployment |

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-org>/XinAn-Med-GraphRAG.git
cd XinAn-Med-GraphRAG

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8024 --reload
```

### Access API Documentation

Open your browser and navigate to:

```
http://localhost:8024/docs
```

### Verify Installation

```bash
# Smoke test
python -c "from backend.main import app; print('Import OK')"

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing
```

### Quick Example

```python
from backend.models.graphrag_engine import GraphRAGEngine

engine = GraphRAGEngine()

# Query the knowledge graph
result = engine.query("汪机擅长治疗什么证型？")
print(result["answer"])

# Search for entities
matches = engine.kg.search("参苓白术散")
print(f"Found: {matches}")

# Get graph statistics
stats = engine.kg.stats()
print(f"Nodes: {stats['nodes']}, Edges: {stats['edges']}, Density: {stats['density']}")
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | `GET` | Service health check and version info |
| `/api/query` | `POST` | GraphRAG question answering (NER + retrieve + generate) |
| `/api/graph/stats` | `GET` | Knowledge graph statistics (node/edge count, density) |
| `/api/graph/search` | `GET` | Search graph entities by keyword |

### Example: Knowledge Graph Query

```bash
curl -X POST http://localhost:8024/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "参苓白术散由哪些药材组成？", "top_k": 8}'
```

### Example: Graph Search

```bash
curl "http://localhost:8024/api/graph/search?q=汪机&limit=10"
```

### Example: Graph Statistics

```bash
curl http://localhost:8024/api/graph/stats
```

## Project Structure

```
XinAn-Med-GraphRAG/
|-- .github/
|   +-- workflows/
|       +-- ci.yml                     # GitHub Actions CI pipeline
|-- backend/
|   |-- __init__.py
|   |-- main.py                        # FastAPI application entry point
|   |-- config.py                      # Application configuration
|   |-- api/
|   |   |-- __init__.py
|   |   |-- query.py                   # GraphRAG query endpoint
|   |   +-- graph.py                   # Knowledge graph stats & search
|   |-- models/
|   |   |-- __init__.py
|   |   |-- xinan_kg.py               # XinAn Knowledge Graph (120+ nodes)
|   |   |-- graphrag_engine.py         # BM25 + Graph RAG pipeline
|   |   |-- ancient_ner.py             # Ancient Chinese medical NER
|   |   |-- terminology_aligner.py     # Ancient-to-modern term alignment
|   |   +-- ancient_text_processor.py  # Text preprocessing
|   |-- analysis/                      # Analysis module (placeholder)
|   |-- data/                          # Data loading module (placeholder)
|   +-- tests/
|       |-- test_kg.py                 # Knowledge graph tests
|       +-- test_expansion_smoke.py    # NER + alignment integration tests
|-- data/
|   +-- xinan_sources.yaml            # Data source registry
|-- docs/
|   |-- Claim_Evidence_Table.md        # Research claim-evidence mapping
|   |-- SCI_Paper_Skeleton.md          # Manuscript outline
|   +-- 技术交底书.md                    # Technical disclosure document
|-- scripts/
|   +-- quick_smoke_test.py            # Quick validation script
|-- tests/
|   |-- __init__.py
|   +-- test_smoke.py                  # Top-level smoke tests
|-- graph_export.json                  # Exported knowledge graph snapshot
|-- pyproject.toml                     # Project metadata & dependencies
|-- requirements.txt                   # Pinned runtime dependencies
|-- Dockerfile                         # Docker container definition
|-- docker-compose.yml                 # Docker Compose orchestration
|-- REPRODUCE.md                       # Reproduction instructions
|-- TODO.md                            # Task tracking and innovation ideas
|-- INNOVATION_ROADMAP.md              # Innovation and patent roadmap
|-- OPTIMIZATION_REPORT.md             # Project optimization report
+-- .gitignore
```

## Knowledge Graph Overview

The XinAn Knowledge Graph encodes the following entity types and relationships:

| Entity Type | Count | Examples |
|------------|-------|---------|
| **Medical Masters** | 20+ | Wang Ji (汪机), Sun Yikui (孙一奎), Cheng Guopeng (程国彭) |
| **Classic Formulas** | 30+ | Shen Ling Bai Zhu San, Liu Wei Di Huang Wan, Bu Zhong Yi Qi Tang |
| **Herbs** | 60+ | Ren Shen, Huang Qi, Bai Zhu, Fu Ling |
| **Syndromes** | 20+ | Spleen-Stomach Deficiency, Qi-Blood Dual Deficiency |
| **Academic Schools** | 15+ | Peiyuan School, Wenbu School, Shanghan School |
| **Classical Texts** | 20+ | Shi Shan Yi An, Chi Shui Xuan Zhu, Yi Xue Xin Wu |

| Relationship Type | Example |
|-------------------|---------|
| Representative Master | XinAn Medicine --[representative master]--> Wang Ji |
| Classic Formula | XinAn Medicine --[classic formula]--> Shen Ling Bai Zhu San |
| Formula Composition | Shen Ling Bai Zhu San --[contains]--> Ren Shen |
| Syndrome Indication | Shen Ling Bai Zhu San --[treats]--> Spleen-Stomach Deficiency |
| Academic School | Peiyuan School --[founder]--> Wang Ji |
| Author | Shi Shan Yi An --[author]--> Wang Ji |

## Benchmarks

> Benchmarks are pending. Results will be published upon completion of evaluation on XinAn medical question-answering test sets.

| Metric | NER Precision | Retrieval Recall | Answer Accuracy |
|--------|--------------|-----------------|----------------|
| Ancient Text NER | Pending | N/A | N/A |
| GraphRAG Query | N/A | Pending | Pending |
| Terminology Alignment | Pending | N/A | N/A |

## Research

This project supports the following research directions:

- **Target Journals**: Data Analysis and Knowledge Discovery (数据分析与知识发现) / Information Science (情报科学)
- **Paper Skeleton**: See `docs/SCI_Paper_Skeleton.md`
- **Claim-Evidence Table**: See `docs/Claim_Evidence_Table.md`
- **Technical Disclosure**: See `docs/技术交底书.md`

## Roadmap

- [ ] Integrate LLM-based generation (replace template-based answers with LLM synthesis)
- [ ] Expand knowledge graph with additional XinAn medical texts and clinical case records
- [ ] Implement graph embedding models (TransE, RotatE) for link prediction
- [ ] Add support for multi-turn dialogue and context-aware follow-up queries
- [ ] Implement vector database integration (FAISS/Milvus) for semantic search
- [ ] Add graph visualization frontend (D3.js / Cytoscape.js)
- [ ] Cross-reference with modern clinical trial data for formula validation
- [ ] Multilingual support for English terminology alignment

## References

The following works informed the design and domain knowledge of this project:

1. Robertson, S. E., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333-389.
2. Ji, S., Pan, S., Cambria, E., Marttinen, P., & Yu, P. S. (2022). A survey on knowledge graphs: Representation, acquisition, and applications. *IEEE Transactions on Neural Networks and Learning Systems*, 33(2), 494-514.
3. Hogan, A., Blomqvist, E., Cochez, M., et al. (2022). Knowledge graphs. *ACM Computing Surveys*, 54(4), 1-37.
4. 朱建平. (2019). 新安医学流派研究. *中华医史杂志*, 49(3), 129-135.
5. 王键, 黄辉. (2014). 新安医学的学术成就与特色. *安徽中医药大学学报*, 33(1), 1-5.
6. 王键. (2009). *新安医学方药与临床*. 北京: 中国中医药出版社.
7. 张志斌, 王致谱. (2010). 新安医家学术思想研究概述. *中医文献杂志*, 28(4), 50-53.

> **Note:** This is a small starter list, not a comprehensive literature review. Contributors are encouraged to expand this section with domain-specific references.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, collaboration, or research inquiries, please open an issue on the repository or contact the project maintainers.
