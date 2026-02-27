"""Streaming pipeline orchestrator for the brochure generator.

Exposes a single ``run_pipeline_stream`` async generator that yields:
  • Stage-progress messages  (e.g. "🔍 Scraping main page…")
  • LLM token chunks         (the actual brochure text, streamed)
  • Error messages            (prefixed with "❌")
"""

import asyncio
import logging
from collections.abc import AsyncGenerator

logger = logging.getLogger("app.task_manager")


async def run_pipeline_stream(url: str) -> AsyncGenerator[str, None]:
    """Execute scrape → clean → generate and **yield** results as they happen.

    Stage updates are yielded as progress strings.  The final brochure is
    yielded token-by-token from the LLM.
    """
    from app.services.brochure_generator.scraper import (
        scrape_main_page,
        filter_related_links,
        scrape_related_pages,
    )
    from app.services.brochure_generator.content_cleaner import combine_and_clean
    from app.services.brochure_generator.llm_summarizer import generate_brochure_stream

    try:
        # --- Step 1: Scrape main page ---
        yield "🔍 Scraping main page…\n\n"
        logger.info("Streaming pipeline – scraping main page: %s", url)
        html, links = await asyncio.to_thread(scrape_main_page, url)

        # --- Step 2: Filter related links ---
        yield "🔗 Filtering related links…\n\n"
        related_urls = filter_related_links(url, links)
        logger.info("Streaming pipeline – found %d related links", len(related_urls))

        # --- Step 3: Scrape related pages ---
        if related_urls:
            yield f"📄 Scraping {len(related_urls)} related page(s)…\n\n"
            related_pages = await asyncio.to_thread(scrape_related_pages, related_urls)
        else:
            yield "📄 No related pages to scrape.\n\n"
            related_pages = []

        # --- Step 4: Clean content ---
        yield "🧹 Cleaning content…\n\n"
        cleaned_text = await asyncio.to_thread(combine_and_clean, html, related_pages)

        # --- Step 5: Generate brochure (streamed from LLM) ---
        yield "✨ Generating brochure…\n\n"
        logger.info("Streaming pipeline – generating brochure via LLM (streaming)")

        # Bridge the sync generator to the async world via a queue.
        # We pass exceptions through the queue (as an _Error sentinel)
        # so they are always retrieved — avoiding "Future exception was
        # never retrieved" warnings.
        queue: asyncio.Queue[str | None | Exception] = asyncio.Queue()

        def _produce() -> None:
            """Run the sync LLM streaming generator and push chunks to the queue."""
            try:
                for token in generate_brochure_stream(cleaned_text):
                    queue.put_nowait(token)
            except Exception as exc:
                queue.put_nowait(exc)  # send the error to the consumer
            finally:
                queue.put_nowait(None)  # sentinel — always signals "done"

        # Run the sync generator in a thread
        asyncio.get_event_loop().run_in_executor(None, _produce)

        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item

        logger.info("Streaming pipeline – completed successfully")

    except Exception as exc:
        logger.exception("Streaming pipeline – failed: %s", exc)
        yield f"\n\n❌ Generation failed: {exc}"
