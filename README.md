<div align="center">

# 🤖 AI Engineering — Projects Hub

**A production-grade FastAPI + Gradio platform for applied AI projects.**
Real-time LLM streaming · Anti-bot web scraping · Map-reduce prompt engineering

---

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.133-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-6.6-FF7C00?logo=gradio&logoColor=white)](https://gradio.app)
[![Gemini](https://img.shields.io/badge/Google_Gemini_3-Flash_Preview-4285F4?logo=google&logoColor=white)](https://aistudio.google.com)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-1C3C3C?logo=chainlink&logoColor=white)](https://langchain.com)

</div>

---

## ✨ What Is This?

This repository is a **multi-project AI engineering platform** — a single FastAPI service that hosts independent AI/ML projects under one roof, each accessible from a unified Gradio UI.

Every project showcases a distinct AI engineering capability: web intelligence, real-time streaming, LLM orchestration, and more.

---

## 🗂️ Project Directory

| # | Project | What it does | Status | Docs |
|---|---------|-------------|--------|------|
| **1** | 🌐 **AI Website Brochure Generator** | Drop in any URL → get a polished marketing brochure. Scrapes up to 11 pages, cleans HTML, and streams a Gemini-powered brochure token-by-token. | ✅ Live | [docs →](docs/ai_website_brochure_generator.md) |

**Lab / Sandbox**: See [lab/README.md](lab/README.md) for Jupyter-based experiments and scratch work before promoting changes into the app.

---

## 🏗️ Platform Architecture

```
┌──────────────────────────────────────────────────┐
│               Gradio UI  (port 8000)             │
│   Home Page ──► Project Pages (async streaming) │
└────────────────────┬─────────────────────────────┘
                     │  mounted on FastAPI
┌────────────────────▼─────────────────────────────┐
│               FastAPI Application                │
│  /api/health          Health check               │
│  /api/project1/stream  SSE brochure stream       │
└────────────────────┬─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│            Service Layer (per project)           │
│  Streaming async generators — no polling         │
│  asyncio.Queue  bridges sync threads → async     │
└──────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### 1 · Clone & create environment

```powershell
git clone <repo-url>
cd "AI Engineering\Projects_1"
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2 · Configure secrets

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
APP_GOOGLE_API_KEY=AIzaSy...          # https://aistudio.google.com/apikey
APP_GEMINI_MODEL=gemini-3-flash-preview
APP_LOG_LEVEL=INFO                    # DEBUG | INFO | WARNING | ERROR | CRITICAL
```

### 3 · Run

```powershell
# Recommended — use the dev script (sets UVICORN_RELOAD_EXCLUDE automatically)
.\dev.ps1

# or via python __main__ (also pre-configured with reload_excludes)
python main.py

# or manually via uvicorn
uvicorn main:app --reload --reload-exclude "logs/*" --reload-exclude "*.log"
```

### 4 · Open

```
http://localhost:8000      # Gradio UI
http://localhost:8000/docs # Interactive API docs (Swagger)
```

---

## 🧾 Logging

- Global structured logging is configured at app startup in `config/logger.py`.
- Request logging is centralized in middleware (`config/middleware.py`) and runs for every route.
- Logs are written to both console and `logs/app.log` (with size-based rotation).
- `X-Request-ID` is accepted from inbound requests (or generated if missing) and echoed back in the response header.

Each request log entry includes:

```json
{
    "timestamp": "",
    "level": "",
    "request_id": "",
    "method": "",
    "path": "",
    "status_code": "",
    "duration_ms": ""
}
```

Request log levels by response status:

- `2xx/3xx` → `INFO`
- `4xx` → `WARNING`
- `5xx` → `ERROR`

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| API framework | **FastAPI 0.133** | Async-first, automatic OpenAPI docs |
| UI | **Gradio 6.6** | Native async generator streaming |
| Web scraping | **Scrapling 0.4** | TLS fingerprint impersonation, anti-bot |
| HTML extraction | **readability-lxml + BeautifulSoup4** | Article-quality text from any page |
| LLM | **LangChain + Google Gemini 3** | `llm.stream()` for token-by-token output |
| Text splitting | **langchain-text-splitters** | Map-reduce for large websites |
| Config | **pydantic-settings** | Type-safe `.env` loading |

---

##  Repository Structure

```
Projects_1/
├── main.py                          # FastAPI app + Gradio mount
├── requirements.txt
├── .env                             # Secrets (gitignored)
│
├── config/
│   ├── settings.py                  # Pydantic settings (env vars)
│   ├── logger.py                    # Structured logging bootstrap
│   └── middleware.py                # Request logging middleware
│
├── routes/
│   ├── api.py                       # API router aggregation
│   └── project1.py                  # POST /api/project1/stream (SSE)
│
├── app/
│   ├── controllers/
│   │   └── project1_controller.py   # Thin async generator pass-through
│   ├── models/
│   │   └── project1_models.py       # Pydantic request schemas
│   └── services/
│       └── brochure_generator/
│           ├── task_manager.py      # Streaming pipeline orchestrator
│           ├── scraper.py           # Multi-page Scrapling scraper
│           ├── content_cleaner.py   # HTML → clean text
│           └── llm_summarizer.py    # Gemini streaming + retry logic
│
├── ui/
│   ├── gradio_app.py                # Main Gradio Blocks interface
│   └── pages/
│       └── project1.py              # Async generator UI page
│
├── lab/
│   ├── README.md                    # How to run lab notebooks
│   └── brochure_playground.ipynb    # Sandbox to try scraper/cleaner/LLM
│
├── logs/
│   └── app.log                      # Runtime logs (gitignored)
│
└── docs/
    └── ai_website_brochure_generator.md
```


<div align="center">

Built with 🧠 and ☕ · Powered by **Google Gemini 3** · Served by **FastAPI**

</div>

