# 🚀 ai-docs-assistant-api

> 🧠 **GenAI (RAG)** • 🐍 **FastAPI** • 🗃️ **PostgreSQL + pgvector** • 🔌 **LangChain + OpenAI** • 🐳 **Docker Compose** • 📨 **Celery + Redis** • 🔐 **API Key**

A production-ready **RAG API** for asking questions about your own documents. Upload PDFs or text, the service chunks and embeds them into **Postgres/pgvector**, then answers queries with **LLM** responses **grounded** in retrieved context (with citations).

---

## ✨ Highlights

* 🗃️ **PostgreSQL + pgvector** for vector search (one source of truth, easy backups)
* 🐍 **FastAPI 0.116+** with OpenAPI docs (`/docs`, `/redoc`)
* 🧱 **LangChain + OpenAI**: `text-embedding-3-small` (default) + chat model (configurable)
* 🧩 **RAG pipeline**: chunking, embedding, ANN retrieval, citations
* 📨 **Asynchroniczny ingest**: **Celery + Redis** (fallback sync w dev)
* 🔐 **Proste auth**: `X-API-Key` header (opcjonalne w DEV)
* 🧪 **Testy** (pytest + httpx) – rekomendowane
* 🐳 **Docker + Compose**: jeden plik, jeden start

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

1. `POST /v1/documents/upload` → ekstrakcja tekstu (PDF/UTF-8)
2. **Ingest**: chunking → embeddings → zapis do `pgvector`
3. `POST /v1/chat/query` → embed zapytania → ANN search → LLM answer + **citations**

---

## 🐳 Quick Start (Docker Compose)

Wymagania: Docker, Docker Compose, klucz do OpenAI.

```bash
# 0) Kopia env
cp .env.example .env
# Edytuj .env i ustaw OPENAI_API_KEY

# 1) Build
docker compose build

# 2) Run (foreground albo -d)
docker compose up
# lub
docker compose up -d

# 3) Logs
docker compose logs -f api
```

Endpoints po starcie:

* API (health): `http://localhost:8080/v1/health`
* Swagger UI: `http://localhost:8080/docs`

Stop & clean:

```bash
docker compose down              # stop
docker compose down -v           # stop + remove volumes (reset DB)
```

> Zmieniłeś kod API?
> `docker compose build api && docker compose up -d`

---

## 🔐 Auth (proste)

Domyślnie używamy nagłówka `X-API-Key`. W DEV można pominąć (gdy `API_KEY` puste).
Dodaj do żądań:

```
X-API-Key: dev-key-123
```

(ustaw w `.env` swoją wartość)

---

## 📚 Endpoints (v1)

### Health

* `GET /v1/health` → status serwisu i DB

### Documents

* `POST /v1/documents/upload` (multipart `file`) → `{ document_id }`
  *Automatycznie próbuje uruchomić ingest (Celery), w DEV spadnie do trybu synchronicznego, jeśli worker nie działa.*
* `POST /v1/documents/{document_id}/ingest` → ręczne uruchomienie ingestu
* `GET  /v1/documents/{document_id}/status` → `uploaded | processing | ready | failed`

### Retrieval (debug)

* `GET /v1/chunks/search?q=...&top_k=5` → podgląd top-K chunków (zawartość + similarity)

### Chat (RAG)

* `POST /v1/chat/query` → `{ answer, citations[] }`
  Body:

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

> Załóżmy `KEY="dev-key-123"` i masz `file.pdf`.

**1) Upload dokumentu**

```bash
curl -s -X POST http://localhost:8080/v1/documents/upload \
  -H "X-API-Key: $KEY" \
  -F "file=@./file.pdf"
# => {"document_id":"<UUID>"}
```

**2) Sprawdź status**

```bash
DOC="<UUID>"
curl -s "http://localhost:8080/v1/documents/$DOC/status" \
  -H "X-API-Key: $KEY"
```

**3) (Opcjonalnie) Wymuś ingest**

```bash
curl -s -X POST "http://localhost:8080/v1/documents/$DOC/ingest" \
  -H "X-API-Key: $KEY"
```

**4) Zapytanie RAG**

```bash
curl -s -X POST http://localhost:8080/v1/chat/query \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d "{\"query\":\"Summarise key points\",\"top_k\":6}"
```

**5) Debug top-K chunków**

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

**Uwaga:**

* Obraz DB w `compose.yaml` to `pgvector/pgvector:pg16` (rozszerzenie `vector` tworzone na starcie).
* Indeks IVFFLAT `vector_cosine_ops` jest zakładany automatycznie (z `lists = 100`).

---

## 🧠 RAG details

* **Chunking:** ok. `1000` znaków, overlap `150` (konfigurowalne)
* **Embeddings:** `text-embedding-3-small` (dim `1536`)
* **ANN retrieval:** kNN w pgvector (`cosine`)
* **Answering:** chat LLM (domyślnie `gpt-4o-mini`) z **citations** (snippet + `document_id`, `chunk_index`)
* **Guardrails:** prompt wymusza „odpowiadaj tylko z kontekstu, w razie braku – powiedz, że nie wiesz”

---

## 🧪 Testing

Rekomendowane:

* **pytest** – unit + e2e
* **httpx** – testy API (ASGI)
* **Fakes** dla embedding/LLM (żeby testy nie trafiały do chmury)
* **Migracje**: inicjalizacja schematu przy starcie testów (możesz użyć osobnej instancji Postgresa lub tymczasowego vol ume)

Przykryj:

* parsowanie PDF/tekstów
* chunking (rozmiar/overlap)
* retrieval (zapytania → top-K)
* ścieżka upload → ingest → query (e2e)

---

## 📊 Observability

* **Structured logs** (JSON-friendly) z `request_id` (do rozbudowy)
* (Nice-to-have) **Prometheus** metrics i **OpenTelemetry** traces (API → retrieval → LLM)

---

## 🧭 Troubleshooting

* `HTTP 500` przy query → sprawdź `OPENAI_API_KEY` i dostęp do modeli
* `failed` status ingestu → upewnij się, że dokument ma tekst (skanowane PDFy wymagają OCR – patrz „Roadmap”)
* Brak wektorów → upewnij się, że `CREATE EXTENSION vector` zostało wykonane (aplikacja robi to przy starcie)
* Worker nie działa → ingest wykona się **synchronicznie** w procesie API (wolniej, ale nie blokuje demo)

---

## 🗺️ Roadmap (nice-to-have)

* 🔎 **Reranking** (HF cross-encoder / LLM re-rank)
* ➕ **Query expansion** (multi-query)
* 🧾 **Eval harness** (hit\@K, MRR, LLM-graded faithfulness)
* 🏷️ **Multi-tenant** (`tenant_id` w każdej tabeli)
* 🚦 **Rate limiting** (Redis) i audyt zapytań
* 🧹 **OCR** (np. Tesseract/TrOCR) dla skanów PDF
* 🔐 **Secret manager** i lepsze polityki PII
* 📈 **Prometheus/Grafana**, **OTel** traces

---

## ⚠️ Notes

* Generowanie embeddingów i odpowiedzi korzysta z zewnętrznych modeli – pamiętaj o **kosztach** i limitach.
* Ten projekt przechowuje tylko **tekst** i **embeddingi**; treści wrażliwe loguj ostrożnie.

---

## 📄 License

MIT (jeśli chcesz, dodam plik `LICENSE`).

---

Chcesz, żebym od razu podmieniła plik `README.md` w Twojej paczce i dorzuciła go do ZIPa pod nową nazwą projektu **ai-docs-assistant-api**?
