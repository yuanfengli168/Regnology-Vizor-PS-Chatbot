# Backend — Vizor PS Chatbot

Python 3.12 + FastAPI + LangChain + ChromaDB.

## First-time setup

```bash
cd backend

# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY, DOCS_FOLDER_PATH, ADMIN_TOKEN

# 4. Run the server
python main.py
```

Server starts at `http://0.0.0.0:8000`. Team URL: `http://192.168.5.48:8000`

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Stream a RAG-powered answer (SSE) |
| `GET` | `/health` | Liveness check |
| `POST` | `/admin/ingest` | Re-index docs from `DOCS_FOLDER_PATH` |
| `POST` | `/admin/stop` | Gracefully shut down the server |

### Chat request format
```json
{
  "session_id": "<uuid>",
  "message": "What is Vizor?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

### Admin endpoints
All admin endpoints require:
```
Authorization: Bearer <ADMIN_TOKEN>
```

---

## Project structure

```
backend/
├── main.py              # FastAPI app + startup lifecycle
├── config.py            # Settings loaded from .env
├── requirements.txt
├── .env.example
├── db/
│   ├── database.py      # SQLAlchemy engine + session
│   └── models.py        # Session + Message tables
├── routers/
│   ├── chat.py          # POST /chat — SSE streaming
│   └── admin.py         # POST /admin/ingest + /admin/stop
└── services/
    ├── rag.py           # ChromaDB retrieval + LLM streaming
    ├── ingest.py        # PDF/Word doc loader + chunker
    └── cache.py         # TTL in-memory cache
```

---

## Auto-start on laptop boot (macOS launchd)

**One-time setup:**
```bash
# Copy the startup script to home (avoids spaces-in-path issues with launchd)
cp launchd/start-backend.sh ~/vizor-start-backend.sh
chmod +x ~/vizor-start-backend.sh

# Register with launchd
cp launchd/com.regnology.vizor-chatbot-backend.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.regnology.vizor-chatbot-backend.plist
```

**Service management:**
```bash
# Status
launchctl list | grep vizor

# Stop
launchctl unload ~/Library/LaunchAgents/com.regnology.vizor-chatbot-backend.plist

# Start
launchctl load ~/Library/LaunchAgents/com.regnology.vizor-chatbot-backend.plist

# Logs
cat /tmp/vizor-backend.log
cat /tmp/vizor-backend-error.log
```

---

## Switching LLM provider

Edit `.env`:
```
OPENAI_MODEL=gpt-4o          # OpenAI (default)
# OPENAI_MODEL=qwen3:14b     # Ollama (future) — also change base_url in rag.py
```

The LangChain abstraction in `services/rag.py` makes this a config-level swap.

---

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | _(required)_ |
| `OPENAI_MODEL` | LLM model name | `gpt-4o` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `DOCS_FOLDER_PATH` | Folder to ingest docs from | `./docs` |
| `ADMIN_TOKEN` | Secret for admin endpoints | _(required)_ |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_db` |
| `DATABASE_URL` | SQLite URL | `sqlite:///./vizor_chat.db` |
| `CACHE_TTL` | Seconds to cache repeated answers | `300` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |

Never commit `.env` — it is gitignored.
