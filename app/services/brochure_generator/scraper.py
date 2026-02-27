"""Scrapling-based web scraping for the brochure generator.

Steps handled here:
  1. Scrape main page & extract internal links
  2. Filter related links (about, services, etc.)
  3. Scrape related pages
"""

import logging
from urllib.parse import urljoin, urlparse

import tldextract
from scrapling.fetchers import Fetcher

logger = logging.getLogger("app.scraper")

# Keywords that indicate a page worth including in the brochure
_RELEVANT_KEYWORDS: set[str] = {
    "about",
    "service",
    "services",
    "product",
    "products",
    "solution",
    "solutions",
    "feature",
    "features",
    "pricing",
    "team",
    "blog",
    "contact",
    "portfolio",
    "company",
    "who-we-are",
    "what-we-do",
    "our-work",
    "careers",
    "clients",
    "customers",
    "case-study",
    "case-studies",
    "testimonials",
}

_MAX_RELATED_PAGES = 10


# ---------------------------------------------------------------------------
# Step 1 – Scrape main page
# ---------------------------------------------------------------------------

def scrape_main_page(url: str) -> tuple[str, list[str]]:
    """Fetch the main page and return (raw_html, list_of_href_links)."""
    logger.info("Fetching main page: %s", url)
    page = Fetcher.get(url, stealthy_headers=True, timeout=30)

    # Raw HTML for later cleaning
    raw_html: str = page.html_content if hasattr(page, "html_content") else str(page)

    # Extract all href values
    raw_links: list[str] = page.css("a::attr(href)").getall()

    # Resolve relative URLs
    absolute_links = [urljoin(url, link) for link in raw_links if link]

    logger.info("Extracted %d links from main page", len(absolute_links))
    return raw_html, absolute_links


# ---------------------------------------------------------------------------
# Step 2 – Filter related links
# ---------------------------------------------------------------------------

def filter_related_links(base_url: str, links: list[str]) -> list[str]:
    """Keep only same-domain links whose path contains relevant keywords."""
    base_ext = tldextract.extract(base_url)
    base_domain = f"{base_ext.domain}.{base_ext.suffix}"

    seen: set[str] = set()
    filtered: list[str] = []

    for link in links:
        # Normalize: strip fragment, trailing slash
        parsed = urlparse(link)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"

        if normalized in seen:
            continue
        seen.add(normalized)

        # Same domain check
        link_ext = tldextract.extract(link)
        link_domain = f"{link_ext.domain}.{link_ext.suffix}"
        if link_domain != base_domain:
            continue

        # Skip non-http(s), anchors-only, file downloads
        if parsed.scheme not in ("http", "https"):
            continue
        if any(parsed.path.lower().endswith(ext) for ext in (".pdf", ".jpg", ".png", ".zip", ".css", ".js")):
            continue

        # Keyword relevance check
        path_lower = parsed.path.lower()
        if any(kw in path_lower for kw in _RELEVANT_KEYWORDS):
            filtered.append(normalized)

        if len(filtered) >= _MAX_RELATED_PAGES:
            break

    logger.info("Filtered to %d related links", len(filtered))
    return filtered


# ---------------------------------------------------------------------------
# Step 3 – Scrape related pages
# ---------------------------------------------------------------------------

def scrape_related_pages(urls: list[str]) -> list[dict[str, str]]:
    """Scrape each related URL and return list of {url, html}."""
    results: list[dict[str, str]] = []
    for url in urls:
        try:
            logger.info("Fetching related page: %s", url)
            page = Fetcher.get(url, stealthy_headers=True, timeout=30)
            raw_html = page.html_content if hasattr(page, "html_content") else str(page)
            results.append({"url": url, "html": raw_html})
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
    return results
