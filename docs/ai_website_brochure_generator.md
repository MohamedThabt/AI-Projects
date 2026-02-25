# AI Website Brochure Generator

## 📌 Project Overview

An **AI-powered website brochure generator** that automatically scrapes website content, discovers related pages, aggregates all data, and uses Google Gemini 3 LLM to generate professional marketing brochures in Markdown format.

**Status:** ✅ **Fully Implemented and Working**

This project demonstrates **AI engineering skills** including:
- Web scraping & crawling with anti-bot bypass
- Data cleaning & preprocessing
- Multi-page content aggregation
- LLM prompt engineering
- Real-time response streaming (SSE + Gradio async generators)
- Async pipeline orchestration and API design
- Agent/system workflow orchestration

---

## 🏗️ Architecture & Implementation

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI 0.133 | REST API with `StreamingResponse` (SSE) |
| **UI** | Gradio 6.6 | Interactive web interface with real-time streaming |
| **Web Scraping** | Scrapling 0.4 (with fetchers) | Multi-page scraping with TLS fingerprint impersonation |
| **HTML Parsing** | BeautifulSoup4, readability-lxml | Extract clean text from HTML |
| **URL Processing** | tldextract | Domain filtering and URL normalization |
| **LLM** | LangChain + Google Gemini 3 Flash Preview | AI brochure generation with token streaming + retry |
| **Text Processing** | langchain-text-splitters | Chunk large content for LLM |
| **Pipeline** | asyncio (Python stdlib) | Streaming async generator pipeline — no task store |

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Gradio UI                                │
│  (URL Input → Async Generator → Live Markdown Streaming)        │
└────────────────────────┬────────────────────────────────────────┘
                         │ Direct service call (no HTTP loopback)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               Service Layer — Streaming Pipeline                 │
│              app/services/brochure_generator/                    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ task_manager.py: run_pipeline_stream() async generator  │    │
│  │  • Yields stage-progress messages immediately           │    │
│  │    "🔍 Scraping…" / "🧹 Cleaning…" / "✨ Generating…"  │    │
│  │  • asyncio.Queue bridges sync thread → async consumer   │    │
│  │  • Errors propagate through queue (no lost futures)     │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                         │
│                         ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ scraper.py: Multi-page web scraping                     │    │
│  │  • Step 1: Fetch main page (Scrapling Fetcher)          │    │
│  │  • Step 2: Extract all links from HTML                  │    │
│  │  • Step 3: Filter same-domain + keyword-relevant links  │    │
│  │    (about, services, products, team, blog, etc.)        │    │
│  │  • Step 4: Scrape up to 10 related pages                │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                         │
│                         ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ content_cleaner.py: Text extraction & cleaning          │    │
│  │  • Uses readability-lxml to extract main article        │    │
│  │  • Strips scripts, styles, nav, footer, headers         │    │
│  │  • Collapses whitespace                                 │    │
│  │  • Combines main + related pages with separators        │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                         │
│                         ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ llm_summarizer.py: AI brochure generation (streaming)   │    │
│  │  • Chunks text (8000 chars, 500 overlap)                │    │
│  │  • Single chunk: Direct streaming LLM call              │    │
│  │  • Multi-chunk: Map-reduce pattern                      │    │
│  │    - Map: Summarize each chunk (non-streamed)           │    │
│  │    - Reduce: Combine summaries → final brochure         │    │
│  │      (final reduce call streams token-by-token)         │    │
│  │  • Retry: 3 attempts, exponential backoff (2s/4s/8s)    │    │
│  │    on 503 / UNAVAILABLE / high-demand errors            │    │
│  │  • Model: gemini-3-flash-preview (temp 0.7)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

        Also available to any HTTP client via SSE:
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Endpoint                              │
│              POST /api/project1/stream (SSE)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Controller Layer                               │
│  handle_generate_stream() — thin async generator pass-through   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 File Structure

```
app/
  controllers/
    project1_controller.py          # Thin async generator pass-through
  models/
    project1_models.py               # Pydantic schemas (BrochureRequest only)
  services/
    brochure_generator/              # Core business logic
      __init__.py                    # Exports run_pipeline_stream
      task_manager.py                # Streaming async generator pipeline
      scraper.py                     # Scrapling-based web scraping
      content_cleaner.py             # HTML → clean text
      llm_summarizer.py              # LangChain + Gemini streaming + retry

routes/
  project1.py                        # POST /stream → SSE StreamingResponse

ui/
  pages/
    project1.py                      # Gradio async generator (direct service call)

config/
  settings.py                        # Environment config (API keys, model)

.env                                 # Secrets (API keys)
requirements.txt                     # Python dependencies
```

---

## 🔄 System Flow (Step-by-Step)

### 1. User Interaction (Gradio UI)
- User enters website URL (e.g., `https://example.com`)
- Clicks "🚀 Generate Brochure"
- Gradio calls the async generator `_generate_brochure(url)` **directly** (no HTTP round-trip)

### 2. Streaming Pipeline Kickoff
- `_generate_brochure()` is an **async generator** — Gradio streams each `yield` live to the `gr.Markdown` component
- It calls `run_pipeline_stream(url)` from the service layer and accumulates chunks into a growing markdown string
- The first visible update appears as soon as scraping starts (typically < 1 second)

### 3. Pipeline Execution — Yielded in Real Time

#### **Step 1: Scrape Main Page**
```python
yield "🔍 Scraping main page…\n\n"
html, links = await asyncio.to_thread(scrape_main_page, url)
```
- Progress message appears in the UI immediately
- Uses Scrapling `Fetcher` (HTTP client with TLS fingerprinting)
- Extracts all `<a href>` links

#### **Step 2: Filter Related Links**
```python
yield "🔗 Filtering related links…\n\n"
related_urls = filter_related_links(url, links)
```
- Same-domain check using `tldextract`
- Keyword matching: `about`, `services`, `products`, `team`, `blog`, `portfolio`, etc.
- Deduplicates URLs, caps at 10 pages

#### **Step 3: Scrape Related Pages**
```python
yield f"📄 Scraping {len(related_urls)} related page(s)…\n\n"
related_pages = await asyncio.to_thread(scrape_related_pages, related_urls)
```
- Fetches each URL with `Fetcher.get()`
- Collects `{"url": str, "html": str}` for each page

#### **Step 4: Clean & Combine Content**
```python
yield "🧹 Cleaning content…\n\n"
cleaned_text = await asyncio.to_thread(combine_and_clean, html, related_pages)
```
- Applies `readability-lxml` to extract main article
- Removes `<script>`, `<style>`, `<nav>`, `<footer>`, etc.
- Collapses whitespace and combines pages with section markers

#### **Step 5: Generate Brochure — Streamed Token-by-Token**
```python
yield "✨ Generating brochure…\n\n"
for token in generate_brochure_stream(cleaned_text):
    yield token  # each LLM token chunk streamed live
```
- **Text chunking:** `RecursiveCharacterTextSplitter` (8000 chars, 500 overlap)
- **Single chunk:** Entire generation streams via `llm.stream(messages)`
- **Multi-chunk (map-reduce):**
  1. **Map phase:** Summarize each chunk (non-streamed — intermediate work)
  2. **Reduce phase:** Combine summaries → final brochure (streamed)
- **Retry logic:** Up to 3 attempts with exponential backoff (2s → 4s → 8s) on transient errors (503 / UNAVAILABLE / high demand)
- **Model:** `gemini-3-flash-preview` (Gemini 3)
- **Prompt engineering:**
  - System: Professional copywriter persona
  - Instructions: Generate brochure with sections (Overview, Services, Highlights, Why Choose Us, Contact)
  - Constraints: Only use provided content, no invention

#### **Error Handling**
- Any exception is `yield`ed as `"\n\n❌ Generation failed: {error}"` — the UI shows it inline
- Exceptions from the LLM producer thread are passed through the `asyncio.Queue` rather than held on a `Future`, preventing "Future exception was never retrieved" warnings

---

## 🛠️ API Endpoints

### `POST /api/project1/stream`

Streams the full pipeline output as **Server-Sent Events (SSE)**. First yields stage-progress messages, then LLM brochure tokens as they arrive.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:** `text/event-stream` — a sequence of SSE `data:` frames:

```
data: 🔍 Scraping main page…

data: 🔗 Filtering related links…

data: 📄 Scraping 7 related page(s)…

data: 🧹 Cleaning content…

data: ✨ Generating brochure…

data: # Acme Corp

data:
## Overview
Acme Corp is a...

data:  leading provider of...

... (token chunks continue)

data: [DONE]
```

**On error**, an error frame is streamed inline before `[DONE]`:
```
data: ❌ Generation failed: 503 UNAVAILABLE

data: [DONE]
```

---

## 🚀 Setup & Usage

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure API Key
Edit `.env`:
```bash
APP_GOOGLE_API_KEY=AIzaSy...  # Your Gemini API key
APP_GEMINI_MODEL=gemini-3-flash-preview
```

Get API key: [Google AI Studio](https://aistudio.google.com/apikey)

### 3. Run Server
```powershell
fastapi dev main.py
```

### 4. Access UI
Open browser: `http://localhost:8000`

---

## 🧪 Testing

### Test via Gradio UI
1. Click "Website Brochure Generator →"
2. Enter URL: `https://example.com`
3. Click "🚀 Generate Brochure"
4. Watch pipeline stages appear live, then brochure text stream in token-by-token

### Test via API
```bash
# curl (bash/WSL)
curl -X POST http://localhost:8000/api/project1/stream \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/project1/stream" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"url": "https://example.com"}'
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'curl_cffi'`
**Fix:** Install `scrapling[fetchers]` instead of just `scrapling`
```powershell
pip install "scrapling[fetchers]"
```

### Issue: `ModuleNotFoundError: No module named 'lxml_html_clean'`
**Fix:** Install separate package
```powershell
pip install lxml_html_clean
```

### Issue: Gemini response is list instead of string
**Fix:** `_extract_text()` helper handles Gemini 3's content format (already implemented)

### Issue: `503 UNAVAILABLE` / `high demand` from Gemini
**Fix:** Automatically retried up to 3 times with exponential backoff (2s → 4s → 8s). If all retries fail, an error message is streamed to the UI.

### Issue: `TypeError: 'Response' object is not subscriptable` / `Future exception was never retrieved`
**Fix:** The LLM producer thread now passes exceptions through the `asyncio.Queue` rather than holding them on an unwaited `Future`. Errors are always surfaced in the UI.

### Issue: Brochure output appears all at once instead of streaming
**Fix:** Ensure the Gradio event handler is wired to an `async def` generator function (not a regular function). The `_generate_brochure()` function must use `yield`, not `return`.

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Time-to-first-byte** | < 1 second (stage message appears immediately) |
| **Time-to-first-LLM-token** | 10-20 seconds (after scraping + cleaning) |
| **Total execution time** | 15-30 seconds |
| **Breakdown:** | |
| - Scraping (1 main + 5-10 pages) | 5-10 seconds |
| - Content cleaning | <1 second |
| - LLM generation (single chunk) | 5-15 seconds |
| - LLM generation (map-reduce) | 10-30 seconds |
| **Retry overhead** | +2s / +4s / +8s per transient LLM error |
| **Concurrent streams** | Unlimited (no shared state, pure generator pipeline) |
| **Memory usage** | ~200 MB per active stream |

---

## 🔮 Future Enhancements

- [ ] **Persistent storage** (Redis/PostgreSQL) for multi-worker deployments
- [ ] **Image extraction** from websites → include in brochure
- [ ] **PDF export** of generated brochures
- [ ] **Stealth mode toggle** (switch to `StealthyFetcher` for JS-heavy sites)
- [ ] **Custom brochure templates** (user-defined section structure)
- [ ] **Multi-language support** (detect website language, generate in same language)
- [ ] **Rate limiting** per user/IP
- [ ] **Caching** of scraped content (avoid re-scraping same URL)

---

## 📝 Lessons Learned

1. **Async FastAPI routes:** Must use `async def` when working with async generators from route handlers
2. **Scrapling dependencies:** Requires `[fetchers]` extra for HTTP client functionality
3. **Gemini 3 response format:** Returns list of content parts, not plain string — need `_extract_text()` helper
4. **readability-lxml split:** `lxml.html.clean` is now a separate package `lxml_html_clean`
5. **Map-reduce for long content:** Essential for websites with >8000 chars of text to fit in LLM context
6. **URL filtering heuristics:** Keyword-based filtering (about/services/etc.) works well vs. ML-based classification (overkill)
7. **Streaming sync generators from async code:** Use `asyncio.Queue` as a bridge — the sync generator runs in `run_in_executor`, pushes items to the queue, and the async consumer `await queue.get()`. Pass exceptions through the queue to avoid "Future exception was never retrieved"
8. **Gradio async generator streaming:** Gradio 6.6 natively streams `async def` generators that `yield` — accumulate chunks into a single string to get a progressively updating output
9. **LLM transient errors:** 503/UNAVAILABLE spikes from Gemini require retry logic; LangChain's built-in `max_retries` does not cover streaming errors — implement retries around the `llm.stream()` call directly

---

## 🎯 Project Goals (All Achieved ✅)

- [x] Multi-page web scraping with link discovery
- [x] Same-domain filtering with intelligent keyword matching
- [x] Clean text extraction (remove nav/footer/scripts)
- [x] LLM integration with Google Gemini 3
- [x] Map-reduce pattern for large content
- [x] Real-time response streaming (SSE API + Gradio async generator)
- [x] Stage-progress updates during pipeline execution
- [x] LLM token-by-token streaming to the UI
- [x] Retry logic with exponential backoff for transient LLM errors
- [x] Professional Markdown brochure output
- [x] Interactive Gradio UI
- [x] Proper error handling surfaced inline to the user