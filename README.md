# AI_Service

FastAPI service.

## Structure

```
/app
	/controllers    # HTTP layer
	/models         # DB & schemas
	/services       # Business logic & AI logic
	/utilities      # Helpers & shared logic

/config           # Settings & environment config
/routes           # Route registration
/ui               # Gradio web interface

main.py           # App entry point
```

## Setup

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run (development)

```powershell
fastapi dev main.py
```

Or with Uvicorn:

```powershell
uvicorn main:app --reload
```

## Environment

Copy `.env.example` to `.env` and edit values as needed.

## Endpoints

- `GET /` - Gradio web interface (main page)
- `GET /api/health` - Health check endpoint
- `POST /api/project1/generate` - Start AI brochure generation (returns task ID)
- `GET /api/project1/status/{task_id}` - Poll brochure generation status

## Projects

This repository contains multiple AI/ML projects:

| Project | Description | Documentation |
|---------|-------------|---------------|
| **AI Website Brochure Generator** | Scrapes websites, extracts content from multiple pages, and uses LLM (Gemini 3) to generate professional marketing brochures in Markdown format | [docs/ai_website_brochure_generator.md](docs/ai_website_brochure_generator.md) |
