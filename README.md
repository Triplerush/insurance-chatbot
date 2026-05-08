# Insurance Chatbot

AI-powered chatbot with Retrieval-Augmented Generation (RAG) for Chilean insurance policies.

The system combines a **LangGraph agent** with **Gemini 2.5 Flash**, **hybrid search** (BM25 + dense embeddings via Haystack/OpenSearch), and **web search** (Tavily) to answer questions about coverage, exclusions, deductibles, and general conditions from real policy documents.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Frontend](#frontend)
- [Evaluation](#evaluation)
- [Docker Reference](#docker-reference)
- [Troubleshooting](#troubleshooting)
- [Tech Stack](#tech-stack)

## Architecture

```
┌─────────────────┐     POST /chat     ┌──────────────────────────────────────┐
│   Frontend      │ ─────────────────► │   Backend (FastAPI)                  │
│   (Streamlit)   │ ◄───────────────── │   ├─ Formatter: mock | gemini       │
│   :8501         │     JSON response  │   │            | langchain ──────┐   │
└─────────────────┘                    │   └─ /health, /docs             │   │
                                       └─────────────────────────────────│───┘
                                                                         │
                                       ┌─────────────────────────────────▼───┐
                                       │   Agent (LangGraph)                 │
                                       │   ├─ Gemini 2.5 Flash (LLM)        │
                                       │   ├─ Query reformulation            │
                                       │   └─ Tools:                         │
                                       │       ├─ hybrid_opensearch_search   │
                                       │       │  (BM25 + embeddings + RRF)  │
                                       │       └─ web_search (Tavily)        │
                                       └──────────────┬─────────────────┬────┘
                                                      │                 │
                                       ┌──────────────▼──┐   ┌─────────▼─────┐
                                       │  OpenSearch      │   │  Tavily API   │
                                       │  :9200           │   │  (web search) │
                                       │  Index: policies │   └───────────────┘
                                       └─────────────────┘
```

The application is composed of four Docker services orchestrated via `docker-compose.yml`:

| Service | Base Image | Port | Description |
|---|---|---|---|
| `backend` | Python 3.11 / FastAPI | `${BACKEND_PORT}` → 8000 | REST API (`/chat`), includes the LangGraph agent |
| `frontend` | Python 3.11 / Streamlit | `${FRONTEND_PORT}` → 8501 | Chat UI with light/dark themes |
| `opensearch` | opensearchproject/opensearch:2.12.0 | 9200, 9600 | Hybrid search engine (BM25 + k-NN) |
| `tasks` | Python 3.11 / Pipeline | — | Data tasks container (ingestion, EDA, evaluation) |

## Prerequisites

- **Docker** and **Docker Compose v2**
- **Gemini API Key** — [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- (Optional) **Tavily API Key** for web search — [https://app.tavily.com/home](https://app.tavily.com/home)
- (Optional) **AWS S3 credentials** for downloading PDFs from a private bucket

## Project Structure

```
.
├── docker-compose.yml
├── .env.example
├── requirements.txt
│
├── services/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── main.py                # FastAPI: /chat, /health, /docs
│   │       └── config.py              # Settings (pydantic-settings)
│   │
│   ├── frontend/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py                     # Streamlit entry point
│   │   ├── core/                      # api, config, state, styles
│   │   └── ui/                        # chat, sidebar, panels, widgets
│   │
│   └── agent/
│       ├── requirements.txt
│       └── app/
│           ├── langchain_runner.py    # AgentRunner entry point
│           ├── graph.py               # LangGraph workflow definition
│           ├── nodes.py               # Graph nodes (model, reformulate, tool)
│           ├── agent_state.py         # Agent state schema
│           ├── prompts.py             # System and reformulation prompts
│           ├── config.py              # AgentSettings (pydantic-settings)
│           └── tools/
│               ├── retrieval/
│               │   └── haystack_opensearch_tool.py
│               └── web_search/
│                   └── web_search.py
│
├── data/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── raw_policies/                  # Source PDFs (downloaded by pipeline)
│   ├── pipeline/
│   │   ├── config.py                  # PipelineSettings
│   │   ├── pipeline.py                # Full orchestrator
│   │   ├── download_from_s3.py        # S3 downloader
│   │   ├── download_public_pdfs.py    # Public PDF downloader
│   │   ├── eda_policies.py            # Exploratory data analysis
│   │   ├── setup_opensearch.py        # Index creation with k-NN mapping
│   │   ├── ingest.py                  # Load → chunk → embed → index
│   │   └── build_policy_summaries.py  # Summaries index (semantic router)
│   └── test/
│       ├── test_opensearch_setup.py
│       └── ragas_eval/
│           ├── run_golden_set.py
│           ├── ragas_metrics.py
│           ├── golden_set/
│           │   ├── golden_set.json
│           │   ├── golden_set_big.json
│           │   └── golden_set_quick.json
│           └── results/
│
├── docs/
│   └── ingest.md
└── eda_out/
    └── eda_recommendations.json
```

## Getting Started

### 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and provide at least the required API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key          # optional
S3_AWS_ACCESS_KEY_ID=your_access_key        # optional
S3_AWS_SECRET_ACCESS_KEY=your_secret_key    # optional
```

All other defaults in `.env.example` are preconfigured for Docker (e.g. `OPENSEARCH_HOST=opensearch`, `INSURANCE_CHATBOT_API_URL=http://backend:8000/chat`).

### 2. Build and start the stack

```bash
docker compose up -d --build
```

This builds and starts all four services. The backend waits for OpenSearch to pass its health check before accepting requests.

### 3. Run the data pipeline

The `tasks` container handles all data operations. The full pipeline performs four steps in sequence: PDF download, OpenSearch index setup, exploratory data analysis, and ingestion.

```bash
# Full pipeline (download + setup + EDA + ingest)
docker compose run --rm tasks python pipeline/pipeline.py

# Skip download (PDFs already in data/raw_policies/)
docker compose run --rm tasks python pipeline/pipeline.py --skip-download

# Skip download and EDA (use CHUNK_SIZE/CHUNK_OVERLAP from .env)
docker compose run --rm tasks python pipeline/pipeline.py --skip-download --skip-eda
```

Individual steps can also be executed independently:

```bash
# Create or recreate the OpenSearch index
docker compose run --rm tasks python pipeline/setup_opensearch.py --recreate

# Run EDA only
docker compose run --rm tasks python pipeline/eda_policies.py

# Run ingestion only (index must already exist)
docker compose run --rm tasks python pipeline/ingest.py

# Run ingestion with index recreation
docker compose run --rm tasks python pipeline/ingest.py --recreate

# Download public Chilean insurance PDFs
docker compose run --rm tasks python pipeline/download_public_pdfs.py

# Build the policy summaries index (semantic router)
docker compose run --rm tasks python pipeline/build_policy_summaries.py --csv path/to/summaries.csv
```

### 4. Verify ingestion

```bash
curl -s http://localhost:9200/policies/_count
curl -s http://localhost:9200/_cluster/health
```

### 5. Access the application

| Service | URL |
|---|---|
| Frontend (Chat UI) | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| OpenSearch | http://localhost:9200 |

## Configuration

All variables are defined in `.env` and injected into containers via the `env_file` directive in `docker-compose.yml`.

### OpenSearch

| Variable | Default | Description |
|---|---|---|
| `OPENSEARCH_VERSION` | `2.12.0` | OpenSearch Docker image version |
| `OPENSEARCH_HOST` | `opensearch` | OpenSearch hostname (Docker service name) |
| `OPENSEARCH_PORT` | `9200` | OpenSearch HTTP port |
| `OPENSEARCH_INDEX` | `policies` | Primary index name |
| `OPENSEARCH_EMBED_DIM` | `384` | Embedding dimension (must match the model) |
| `OPENSEARCH_USER` | `admin` | OpenSearch username |
| `OPENSEARCH_PASSWORD` | `admin` | OpenSearch password |

### API Keys

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (required for `langchain` and `gemini` formatters) |
| `TAVILY_API_KEY` | Tavily API key (optional, enables web search) |

### Backend

| Variable | Default | Description |
|---|---|---|
| `BACKEND_PORT` | `8000` | Exposed backend port |
| `INSURANCE_CHATBOT_FORMATTER` | `langchain` | Response strategy: `mock`, `gemini`, or `langchain` |
| `INSURANCE_CHATBOT_LANGCHAIN_RUNNER` | `agent.app.langchain_runner:run_langchain_agent` | Agent runner module path |

### Frontend

| Variable | Default | Description |
|---|---|---|
| `FRONTEND_PORT` | `8501` | Exposed frontend port |
| `INSURANCE_CHATBOT_API_URL` | `http://backend:8000/chat` | Backend `/chat` endpoint URL |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Run Streamlit without opening a browser |

### Gemini

| Variable | Default | Description |
|---|---|---|
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier |
| `GEMINI_TEMPERATURE` | `0.2` | Generation temperature |
| `GEMINI_TOP_P` | `0.95` | Top-p sampling |
| `GEMINI_MAX_OUTPUT_TOKENS` | `1024` | Maximum output tokens |

### Agent Tools

| Variable | Default | Description |
|---|---|---|
| `WEB_SEARCH_MAX_RESULTS` | `5` | Maximum Tavily results per query |
| `WEB_SEARCH_FRESHNESS_DAYS` | `30` | Prefer results within N days |
| `RETRIEVAL_TOP_K` | `40` | Documents to retrieve per BM25/embedding channel |

### Embeddings and Ingestion

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `CHUNK_SIZE` | `1000` | Chunk size in characters |
| `CHUNK_OVERLAP` | `240` | Overlap between chunks |
| `PDF_DIR` | `./data/raw_policies` | Source PDF directory |
| `POLICY_SUMMARIES_INDEX` | `policy_summaries_index` | Summaries index for the semantic router |

### S3

| Variable | Description |
|---|---|
| `S3_AWS_ACCESS_KEY_ID` | AWS Access Key ID |
| `S3_AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key |

## API Reference

### Formatter Selection

The backend resolves the response strategy through `INSURANCE_CHATBOT_FORMATTER`:

| Value | Behavior |
|---|---|
| `mock` | Returns static text. No external API calls. Useful for infrastructure testing. |
| `gemini` | Calls Gemini directly with retrieved contexts. No autonomous tool usage. |
| `langchain` | Runs the full LangGraph agent with hybrid retrieval and optional web search. **(Recommended)** |

When using `langchain`, the agent executes a graph with three node types:

1. **`call_model_node`** — Invokes Gemini with bound tools, system prompt, conversation history, and accumulated context.
2. **`reformulate_for_tools_node`** — Rewrites ambiguous tool queries using conversation history for better retrieval.
3. **`call_tool_node`** — Executes tools in parallel (`hybrid_opensearch_search`, `web_search`). The loop repeats up to 3 iterations.

### `POST /chat`

#### Request

```json
{
  "messages": [
    { "role": "user", "content": "¿Qué cubre la póliza de hogar?" },
    { "role": "assistant", "content": "Previous response..." },
    { "role": "user", "content": "¿Y los cristales?" }
  ],
  "top_k": 4,
  "enable_web_search": false,
  "debug": false,
  "language": "es"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `messages` | `Message[]` | required | Ordered conversation history. The last message must have `role: "user"`. |
| `top_k` | `integer` | `4` | Number of fragments to retrieve (1–10). |
| `enable_web_search` | `boolean` | `false` | Enable web search (requires `TAVILY_API_KEY`). |
| `debug` | `boolean` | `false` | Include the `debug` block in the response. |
| `language` | `string` | `"es"` | Response language. |
| `metadata` | `object` | `null` | Free-form client metadata. |

#### Response

```json
{
  "answer": "Sí, la póliza cubre cristales. Según las Condiciones Generales...",
  "sources": [
    {
      "title": "mapfre_cristales.pdf",
      "snippet": "La póliza cubre la rotura accidental de cristales...",
      "file_name": "mapfre_cristales.pdf",
      "page": 3,
      "chunk_id": 12,
      "score": 0.87
    }
  ],
  "usage": {
    "retrieved_documents": 5,
    "web_search_enabled": false,
    "formatter": "langchain",
    "language": "es",
    "top_k": 4,
    "debug_enabled": false
  }
}
```

| Field | Type | Description |
|---|---|---|
| `answer` | `string` | Generated response text. |
| `sources` | `Source[]` | Retrieved documents with metadata (title, snippet, file, page, score). |
| `usage` | `object` | Diagnostic metrics. |
| `debug` | `object` | Present only when `debug: true`. Contains agent steps, timings, and tool invocations. |

#### Debug Response Example

When `debug: true` is passed, the response includes execution details:

```json
{
  "debug": {
    "total_duration_ms": 3421.55,
    "steps": [
      { "step": "call_model_node", "duration_ms": 1200.3 },
      { "step": "reformulate_for_tools_node", "duration_ms": 800.1 },
      { "step": "call_tool", "tool": "hybrid_opensearch_search", "duration_ms": 450.2 },
      { "step": "call_model_node", "duration_ms": 970.9 }
    ],
    "chunks": [],
    "tool_iterations": 1
  }
}
```

#### Example

```bash
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
        "messages": [
          {"role": "user", "content": "¿Qué cubre la póliza de hogar básica?"}
        ],
        "top_k": 4,
        "enable_web_search": false,
        "debug": true,
        "language": "es"
      }'
```

### `GET /health`

Returns `{"status": "ok"}` when the service is running.

### `GET /docs`

Swagger UI with the full API schema.

## Frontend

The Streamlit frontend (`services/frontend/`) provides:

- Interactive chat with conversation history.
- Light and dark theme selection via the sidebar.
- Configurable sidebar: API URL, `top_k`, web search toggle, debug mode, language.
- Information panels:
  - **Sources** — retrieved documents with file name, page, and relevance score.
  - **Metrics** — number of retrieved documents, active formatter, latency.
  - **Debug** — agent steps, invoked tools, and per-step timings (requires debug mode).
- Quick-access suggestion buttons for common queries.

## Evaluation

The `tasks` container includes an automated evaluation system using [RAGAS](https://docs.ragas.io/) metrics (`faithfulness` and `context_precision`).

### Running the evaluation

```bash
# Standard golden set (35 scenarios across 5 categories)
docker compose run --rm tasks python test/ragas_eval/run_golden_set.py \
  --base-url http://backend:8000/chat \
  --golden-set test/ragas_eval/golden_set/golden_set.json

# Quick golden set (fewer scenarios, for fast iteration)
docker compose run --rm tasks python test/ragas_eval/run_golden_set.py \
  --base-url http://backend:8000/chat \
  --golden-set test/ragas_eval/golden_set/golden_set_quick.json

# Compare against a previous baseline
docker compose run --rm tasks python test/ragas_eval/run_golden_set.py \
  --base-url http://backend:8000/chat \
  --baseline-metrics results/golden_before.metrics.json
```

The golden set covers five scenario categories: `simple`, `follow_up`, `web`, `combined`, and `negative`.

Results are saved to `data/test/ragas_eval/results/` (mounted as a Docker volume).

## Docker Reference

```bash
# Build and start all services
docker compose up -d --build

# Follow logs
docker compose logs -f
docker compose logs -f backend

# Restart a specific service
docker compose restart backend

# Stop all services
docker compose down

# Stop and remove volumes (deletes OpenSearch data)
docker compose down -v

# Rebuild a single service
docker compose build backend
docker compose up -d backend

# Run tests
docker compose run --rm tasks pytest -q

# Open an interactive shell in the tasks container
docker compose run --rm tasks bash
```

## Troubleshooting

### OpenSearch fails to start or remains unhealthy

```bash
docker compose logs -f opensearch
curl -s http://localhost:9200/_cluster/health
```

OpenSearch may take 30–60 seconds to become ready. The backend has a `depends_on` directive with `condition: service_healthy` and will wait automatically.

Verify that ports `9200` and `9600` are not in use by another process.

### Backend does not respond

```bash
docker compose ps
docker compose logs -f backend
curl -s http://localhost:8000/health
```

### Embedding dimension mismatch

If the embedding model is changed, the following steps are required:

1. Update `OPENSEARCH_EMBED_DIM` to match the new model's output dimension.
2. Recreate the index:
   ```bash
   docker compose run --rm tasks python pipeline/setup_opensearch.py --recreate
   ```
3. Re-ingest the documents:
   ```bash
   docker compose run --rm tasks python pipeline/ingest.py
   ```

### Web search returns no results

- Verify that `TAVILY_API_KEY` is set correctly in `.env`.
- Verify that `enable_web_search` is set to `true` in the request payload.
- The agent only invokes web search when:
  - The query mixes an external event with a policy question, **or**
  - The internal search returned insufficient results.

### Gemini rate limiting (HTTP 429)

The agent handles 429 errors from Gemini gracefully and returns a message indicating that the user should wait before retrying.

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Agent framework | LangGraph + LangChain |
| Hybrid search | Haystack 2.x + OpenSearch (BM25 + k-NN + RRF) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (384 dims) |
| Web search | Tavily API |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Vector store | OpenSearch 2.12.0 |
| Containers | Docker + Docker Compose v2 |
| Evaluation | RAGAS (faithfulness, context_precision) |
| Runtime | Python 3.11 |
