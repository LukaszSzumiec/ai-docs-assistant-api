# 🚀 ai-docs-assistant-api

> 🧠 **GenAI (RAG)** • 🐍 **FastAPI** • 🗃️ **PostgreSQL + pgvector** • 🔌 **LangChain + OpenAI** • 🐳 **Docker Compose** • 📨 **Celery + Redis** • 🔐 **API Key**

A modern, production-ready **RAG API** for querying your own documents. Upload PDFs or text, the service chunks and embeds them into **Postgres/pgvector**, then answers questions with **LLM** responses grounded in retrieved context (with citations).

---

## ✨ Highlights

* 🗃️ **PostgreSQL + pgvector** for vector search (single source of truth, easy backups)
* 🐍 **FastAPI** with OpenAPI docs (`/docs`, `/redoc`)
* 🔌 **LangChain + OpenAI**: `text-embedding-3-small` (default) + configurable chat model
* 🧩 **RAG pipeline**: chunking, embeddings, ANN retrieval, citations
* 📨 **Async ingestion**: **Celery + Redis** (sync fallback in dev)
* 🔐 **Simple auth**: `X-API-Key` header (optional in dev)
* 🐳 **Docker Compose**: one file, one command

**API Docs:**

* 🧭 Swagger UI → `http://localhost:8080/docs`
* 📜 OpenAPI JSON → `http://localhost:8080/openapi.json`

---

## 🏗️ Architecture

```
ai-docs-assistant-api/
├── app/
│   ├── api/                 🎮 Endpoints (routers, deps)
│   ├── core/                🔧 Config, logging
│   ├── db/                  🗄️ SQLAlchemy models, init, repos
│   ├── ingestion/           📥 Parsers + Celery tasks/worker
│   └── rag/                 🧠 Chunker, embeddings, retriever, pipeline, prompts
├── docker/
│   ├── api/Dockerfile       🐳 API image
│   └── worker/Dockerfile    🐳 Celery worker image
├── compose.yaml             🧩 Postgres+pgvector, Redis, API, Worker
├── pyproject.toml           📦 Dependencies & tooling
└── README.md                📘 This file
```

**RAG flow (high level):**

1. `POST /v1/documents/upload` → extract text (PDF/UTF-8)
2. **Ingest**: chunking → embeddings → store in `pgvector`
3. `POST /v1/chat/query` → embed question → ANN search → LLM answer + **citations**

---

## 🐳 Quick Start (Docker Compose)

Requirements: Docker, Docker Compose, an OpenAI API key.

```bash
# 0) Configure environment
cp .env.example .env
# edit .env and set OPENAI_API_KEY

# 1) Build
docker compose build

# 2) Run (foreground or -d)
docker compose up
# or
docker compose up -d

# 3) Tail logs
docker compose logs -f api
```

Endpoints after startup:

* Health: `http://localhost:8080/v1/health`
* Swagger UI: `http://localhost:8080/docs`

Stop & clean:

```bash
docker compose down              # stop
docker compose down -v           # stop + remove volumes (reset DB)
```

> Changed the API code?
> `docker compose build api && docker compose up -d`

---

## 🔐 Auth

By default the API expects `X-API-Key`. In dev you can leave it empty to disable auth.

```
X-API-Key: dev-key-123
```

Configure in `.env`.

---

## 📚 Endpoints (v1)

### Health

* `GET /v1/health` → service & DB status

### Documents

* `POST /v1/documents/upload` (multipart `file`) → `{ "document_id": "<UUID>" }`
  *Automatically tries Celery ingestion; in dev falls back to sync if the worker is down.*
* `POST /v1/documents/{document_id}/ingest` → force ingestion
* `GET  /v1/documents/{document_id}/status` → `uploaded | processing | ready | failed`

### Retrieval (debug)

* `GET /v1/chunks/search?q=...&top_k=5` → preview top-K chunks (content + similarity)

### Chat (RAG)

* `POST /v1/chat/query` → `{ "answer": "...", "citations": [...] }`
  Request body:

  ```json
  {
    "query": "What is X?",
    "top_k": 6,
    "temperature": 0.0,
    "max_tokens": 400,
    "document_ids": ["...optional..."]
  }
  ```

---

## 🧰 Example cURL

Assume `KEY="dev-key-123"` and you have `file.pdf`.

**1) Upload a document**

```bash
curl -s -X POST http://localhost:8080/v1/documents/upload \
  -H "X-API-Key: $KEY" \
  -F "file=@./file.pdf"
# => {"document_id":"<UUID>"}
```

**2) Check status**

```bash
DOC="<UUID>"
curl -s "http://localhost:8080/v1/documents/$DOC/status" \
  -H "X-API-Key: $KEY"
```

**3) (Optional) Force ingestion**

```bash
curl -s -X POST "http://localhost:8080/v1/documents/$DOC/ingest" \
  -H "X-API-Key: $KEY"
```

**4) Ask a question (RAG)**

```bash
curl -s -X POST http://localhost:8080/v1/chat/query \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d "{\"query\":\"Summarise key points\",\"top_k\":6}"
```

**5) Debug top-K chunks**

```bash
curl -s "http://localhost:8080/v1/chunks/search?q=topic&top_k=5" \
  -H "X-API-Key: $KEY"
```

---

## ⚙️ Configuration (.env)

```env
APP_ENV=dev
API_TITLE=ai-docs-assistant-api
API_VERSION=0.1.0

# OpenAI
OPENAI_API_KEY=sk-...
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBED_DIM=1536

# Postgres + pgvector
DB_DSN=postgresql+psycopg://docs:docs@db:5432/docs

# Celery / Redis
REDIS_URL=redis://redis:6379/0
CELERY_CONCURRENCY=2

# Auth
API_KEY=dev-key-123

# Retrieval / Chunking
TOP_K=6
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

Notes:

* DB image in `compose.yaml` is `pgvector/pgvector:pg16` (the `vector` extension is created on startup).
* An IVFFLAT `vector_cosine_ops` index is created automatically (`lists = 100`).

---

## 🧠 RAG Details

* **Chunking:** \~`1000` chars, overlap `150` (configurable)
* **Embeddings:** `text-embedding-3-small` (dim `1536`)
* **ANN retrieval:** k-NN with cosine distance in pgvector
* **Answering:** chat LLM (default `gpt-4o-mini`) with **citations** (snippet + `document_id`, `chunk_index`)
* **Guardrails:** prompt instructs “answer only from context; otherwise say you don’t know”

---

## 🧪 Testing (recommended)

* **pytest** – unit + e2e
* **httpx** – ASGI API tests
* **Fakes** for embeddings/LLM to avoid external calls in CI
* Cover: PDF/text parsing, chunking, retrieval, end-to-end upload → ingest → query

---

## 📊 Observability

* Structured logs (JSON-friendly) with `request_id` (ready for extension)
* (Nice-to-have) **Prometheus** metrics & **OpenTelemetry** traces (API → retrieval → LLM)

---

## 🧭 Troubleshooting

* `HTTP 500` on `/chat/query` → check `OPENAI_API_KEY` and model access
* `status = failed` after ingest → the document may not contain extractable text (scanned PDFs need OCR)
* No vectors stored → ensure `CREATE EXTENSION vector` ran (the app does this on startup)
* Celery worker down → ingestion falls back to **synchronous** mode (slower but fine for demos)

---

## 🗺️ Roadmap

* 🔎 Reranking (HF cross-encoder / LLM re-rank)
* ➕ Query expansion (multi-query)
* 🧾 Eval harness (hit\@K, MRR, LLM-graded faithfulness)
* 🏷️ Multi-tenant (`tenant_id` across tables)
* 🚦 Rate limiting (Redis) & query audit
* 🧹 OCR (e.g., Tesseract/TrOCR) for scanned PDFs
* 🔐 Secret manager & PII redaction policies
* 📈 Prometheus/Grafana, OpenTelemetry traces

---

## 📄 License

MIT (add a `LICENSE` file if desired).
