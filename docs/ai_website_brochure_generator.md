# AI Website Brochure Generator

## 📌 Project Overview

An **AI-powered website brochure generator** that automatically scrapes website content, discovers related pages, aggregates all data, and uses Google Gemini 3 LLM to generate professional marketing brochures in Markdown format.

**Status:** ✅ **Fully Implemented and Working**

This project demonstrates **AI engineering skills** including:
- Web scraping & crawling with anti-bot bypass
- Data cleaning & preprocessing
- Multi-page content aggregation
- LLM prompt engineering
- Async task management and API design
- Agent/system workflow orchestration

---

## 🏗️ Architecture & Implementation

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI 0.133 | REST API endpoints with async support |
| **UI** | Gradio 6.6 | Interactive web interface |
| **Web Scraping** | Scrapling 0.4 (with fetchers) | Multi-page scraping with TLS fingerprint impersonation |
| **HTML Parsing** | BeautifulSoup4, readability-lxml | Extract clean text from HTML |
| **URL Processing** | tldextract | Domain filtering and URL normalization |
| **LLM** | LangChain + Google Gemini 3 Flash Preview | AI brochure generation |
| **Text Processing** | langchain-text-splitters | Chunk large content for LLM |
| **Task Management** | asyncio (Python stdlib) | Background task orchestration |

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Gradio UI                                │
│  (URL Input → Poll Status → Display Markdown Brochure)          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Endpoints                             │
│  POST /api/project1/generate  →  GET /api/project1/status/{id}  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Controller Layer                               │
│         (Request validation, response shaping)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Service Layer (Package)                         │
│              app/services/brochure_generator/                    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ task_manager.py: Async orchestration & task store       │    │
│  │  • Creates UUID task IDs                                │    │
│  │  • Spawns asyncio background tasks                      │    │
│  │  • Tracks status: pending → scraping → cleaning →       │    │
│  │    generating → completed/failed                        │    │
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
│  │ llm_summarizer.py: AI brochure generation               │    │
│  │  • Chunks text (8000 chars, 500 overlap)                │    │
│  │  • Single chunk: Direct LLM call                        │    │
│  │  • Multi-chunk: Map-reduce pattern                      │    │
│  │    - Map: Summarize each chunk individually             │    │
│  │    - Reduce: Combine summaries → final brochure         │    │
│  │  • Model: gemini-3-flash-preview (temp 0.7)             │    │
│  │  • Output: Professional Markdown brochure               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📂 File Structure

```
app/
  controllers/
    project1_controller.py          # HTTP layer - handles requests
  models/
    project1_models.py               # Pydantic schemas (request/response)
  services/
    brochure_generator/              # Core business logic
      __init__.py                    # Package exports
      task_manager.py                # Async task orchestration
      scraper.py                     # Scrapling-based web scraping
      content_cleaner.py             # HTML → clean text
      llm_summarizer.py              # LangChain + Gemini integration

routes/
  project1.py                        # FastAPI route definitions

ui/
  pages/
    project1.py                      # Gradio UI component

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
- UI calls `POST /api/project1/generate`

### 2. Task Creation (Controller → Service)
- **Route handler** validates URL (Pydantic `HttpUrl`)
- **Controller** calls `start_generation(url)`
- **Task manager** creates UUID task ID, stores task metadata
- Spawns `asyncio.create_task(_run_pipeline(task_id, url))`
- Returns `HTTP 202 Accepted` with task ID immediately

### 3. Background Pipeline Execution (asyncio task)

#### **Step 1: Scrape Main Page**
```python
page = Fetcher.get(url, stealthy_headers=True)
raw_html = page.html_content
links = page.css('a::attr(href)').getall()
```
- Uses Scrapling `Fetcher` (HTTP client with TLS fingerprinting)
- Extracts all `<a href>` links

#### **Step 2: Filter Related Links**
```python
filtered = filter_related_links(base_url, links)
```
- Same-domain check using `tldextract`
- Keyword matching: `about`, `services`, `products`, `team`, `blog`, `portfolio`, etc.
- Deduplicates URLs, caps at 10 pages

#### **Step 3: Scrape Related Pages**
```python
related_pages = scrape_related_pages(filtered_urls)
```
- Fetches each URL with `Fetcher.get()`
- Collects `{"url": str, "html": str}` for each page

#### **Step 4: Clean & Combine Content**
```python
cleaned_text = combine_and_clean(main_html, related_pages)
```
- Applies `readability-lxml` to extract main article
- Removes `<script>`, `<style>`, `<nav>`, `<footer>`, etc.
- Collapses whitespace
- Combines pages with section markers

#### **Step 5: Generate Brochure (LLM)**
```python
brochure_md = generate_brochure(cleaned_text)
```
- **Text chunking:** `RecursiveCharacterTextSplitter` (8000 chars, 500 overlap)
- **Single chunk:** Direct LLM call with system + brochure prompt
- **Multi-chunk:** Map-reduce pattern:
  1. **Map phase:** Summarize each chunk individually
  2. **Reduce phase:** Combine summaries → final brochure
- **Model:** `gemini-3-flash-preview` (Gemini 3)
- **Prompt engineering:**
  - System: Professional copywriter persona
  - Instructions: Generate brochure with sections (Overview, Services, Highlights, Why Choose Us, Contact)
  - Constraints: Only use provided content, no invention

#### **Step 6: Store Result**
```python
task.status = "completed"
task.result = brochure_md  # Markdown string
```

### 4. Status Polling (UI → API)
- UI polls `GET /api/project1/status/{task_id}` every 3 seconds
- Returns `{"status": "scraping_main_page" | "cleaning_content" | "completed", "result": "...", "error": null}`
- When `status == "completed"`, UI renders Markdown brochure

---

## 🛠️ API Endpoints

### `POST /api/project1/generate`

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response (HTTP 202):**
```json
{
  "task_id": "6be4cfb9-7726-4721-b00a-abe445af66bc",
  "status": "pending"
}
```

---

### `GET /api/project1/status/{task_id}`

**Response (In Progress):**
```json
{
  "task_id": "6be4cfb9-...",
  "status": "generating_brochure",
  "result": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "task_id": "6be4cfb9-...",
  "status": "completed",
  "result": "# Company Name\n\n## Overview\n...",
  "error": null
}
```

**Response (Failed):**
```json
{
  "task_id": "6be4cfb9-...",
  "status": "failed",
  "result": null,
  "error": "ModuleNotFoundError: No module named 'curl_cffi'"
}
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
4. Wait 10-30 seconds (polls automatically)
5. View generated Markdown brochure

### Test via API (curl)
```powershell
# Start generation
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/project1/generate" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"url": "https://example.com"}'
$taskId = $response.task_id

# Poll status
Invoke-RestMethod -Uri "http://localhost:8000/api/project1/status/$taskId"
```

---

## 🐛 Troubleshooting

### Issue: `RuntimeError: no running event loop`
**Fix:** Route handlers must be `async def` (fixed in implementation)

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
**Fix:** Use `_extract_text()` helper to handle Gemini 3's content format (already implemented)

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Average execution time** | 15-30 seconds |
| **Breakdown:** | |
| - Scraping (1 main + 5-10 pages) | 5-10 seconds |
| - Content cleaning | <1 second |
| - LLM generation (single chunk) | 5-15 seconds |
| - LLM generation (map-reduce) | 10-30 seconds |
| **Concurrent tasks** | Unlimited (in-memory store, single process) |
| **Memory usage** | ~200 MB per task |

---

## 🔮 Future Enhancements

- [ ] **Persistent task storage** (Redis/PostgreSQL) for multi-worker deployments
- [ ] **Image extraction** from websites → include in brochure
- [ ] **PDF export** of generated brochures
- [ ] **Stealth mode toggle** (switch to `StealthyFetcher` for JS-heavy sites)
- [ ] **Custom brochure templates** (user-defined section structure)
- [ ] **Multi-language support** (detect website language, generate in same language)
- [ ] **Rate limiting** per user/IP
- [ ] **Webhook notifications** instead of polling
- [ ] **Caching** of scraped content (avoid re-scraping same URL)

---

## 📝 Lessons Learned

1. **Async FastAPI routes:** Must use `async def` when calling `asyncio.create_task()` from route handlers
2. **Scrapling dependencies:** Requires `[fetchers]` extra for HTTP client functionality
3. **Gemini 3 response format:** Returns list of content parts, not plain string — need extraction helper
4. **readability-lxml split:** `lxml.html.clean` is now separate package `lxml_html_clean`
5. **Map-reduce for long content:** Essential for websites with >8000 chars of text to fit in LLM context
6. **URL filtering heuristics:** Keyword-based filtering (about/services/etc.) works well vs. ML-based classification (overkill)

---

## 🎯 Project Goals (All Achieved ✅)

- [x] Multi-page web scraping with link discovery
- [x] Same-domain filtering with intelligent keyword matching
- [x] Clean text extraction (remove nav/footer/scripts)
- [x] LLM integration with Google Gemini 3
- [x] Map-reduce pattern for large content
- [x] Async task management with polling API
- [x] Professional Markdown brochure output
- [x] Interactive Gradio UI
- [x] Proper error handling and status tracking