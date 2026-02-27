"""Combine and clean scraped HTML content.

Takes raw HTML from the main page and related pages, extracts readable text,
and produces a single cleaned text blob ready for the LLM.
"""

import logging
import re

from readability import Document as ReadabilityDocument
from bs4 import BeautifulSoup

logger = logging.getLogger("app.content_cleaner")


def _extract_text_from_html(html: str) -> str:
    """Use readability-lxml to get main content, then strip remaining tags."""
    try:
        doc = ReadabilityDocument(html)
        summary_html = doc.summary()
        title = doc.title()
    except Exception:
        # Fallback: just use raw HTML
        summary_html = html
        title = ""

    soup = BeautifulSoup(summary_html, "html.parser")

    # Remove script, style, nav, footer, header tags
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    if title:
        text = f"# {title}\n\n{text}"

    return text.strip()


def combine_and_clean(main_html: str, related_pages: list[dict[str, str]]) -> str:
    """Merge main page + related pages into one cleaned text document.

    Parameters
    ----------
    main_html : str
        Raw HTML of the main page.
    related_pages : list[dict[str, str]]
        Each dict has keys ``url`` and ``html``.

    Returns
    -------
    str
        A single cleaned text blob.
    """
    sections: list[str] = []

    # Main page
    main_text = _extract_text_from_html(main_html)
    if main_text:
        sections.append(f"=== MAIN PAGE ===\n{main_text}")

    # Related pages
    for page in related_pages:
        page_text = _extract_text_from_html(page["html"])
        if page_text:
            sections.append(f"=== PAGE: {page['url']} ===\n{page_text}")

    combined = "\n\n---\n\n".join(sections)
    logger.info("Combined cleaned text length: %d characters", len(combined))
    return combined
