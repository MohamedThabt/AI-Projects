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
