import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Task store (in-memory, single-process)
# ---------------------------------------------------------------------------

@dataclass
class TaskInfo:
    task_id: str
    url: str
    status: str = "pending"
    result: str | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


_tasks: dict[str, TaskInfo] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_generation(url: str) -> str:
    """Create a new brochure-generation task and return its ID."""
    task_id = str(uuid.uuid4())
    _tasks[task_id] = TaskInfo(task_id=task_id, url=url)
    asyncio.create_task(_run_pipeline(task_id, url))
    return task_id


def get_task_status(task_id: str) -> TaskInfo | None:
    """Return the current state of a task, or *None* if not found."""
    return _tasks.get(task_id)


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

async def _run_pipeline(task_id: str, url: str) -> None:
    """Execute the full scrape → clean → generate pipeline."""
    from app.services.brochure_generator.scraper import (
        scrape_main_page,
        filter_related_links,
        scrape_related_pages,
    )
    from app.services.brochure_generator.content_cleaner import combine_and_clean
    from app.services.brochure_generator.llm_summarizer import generate_brochure

    task = _tasks[task_id]

    try:
        # --- Step 1-2: Scrape main page & extract links ---
        task.status = "scraping_main_page"
        logger.info("Task %s – scraping main page: %s", task_id, url)
        html, links = await asyncio.to_thread(scrape_main_page, url)

        # --- Step 3: Filter related links ---
        task.status = "filtering_links"
        related_urls = filter_related_links(url, links)
        logger.info("Task %s – found %d related links", task_id, len(related_urls))

        # --- Step 4: Scrape related pages ---
        task.status = "scraping_related_pages"
        related_pages = await asyncio.to_thread(scrape_related_pages, related_urls)

        # --- Step 5: Combine & clean ---
        task.status = "cleaning_content"
        cleaned_text = combine_and_clean(html, related_pages)

        # --- Step 6: LLM brochure generation ---
        task.status = "generating_brochure"
        logger.info("Task %s – generating brochure via LLM", task_id)
        brochure_md = await asyncio.to_thread(generate_brochure, cleaned_text)

        task.status = "completed"
        task.result = brochure_md
        logger.info("Task %s – completed successfully", task_id)

    except Exception as exc:
        task.status = "failed"
        task.error = str(exc)
        logger.exception("Task %s – failed: %s", task_id, exc)
