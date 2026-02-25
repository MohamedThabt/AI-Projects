"""LangChain + Google Gemini brochure generation.

Takes cleaned website text, chunks it if needed, and uses an LLM to produce
a professional brochure in Markdown format.
"""

import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import settings

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 8_000
_CHUNK_OVERLAP = 500

_BROCHURE_SYSTEM_PROMPT = """\
You are a professional copywriter and marketing expert. Your task is to create \
a polished, engaging **brochure** in Markdown format based on the website content \
provided.

The brochure MUST include the following sections (skip any section if there is \
truly no relevant information):

1. **Company Overview** – Who they are, mission, and value proposition.
2. **Products & Services** – What they offer, key features.
3. **Key Highlights** – Awards, stats, differentiators, testimonials.
4. **Why Choose Us** – Competitive advantages.
5. **Contact Information** – Address, phone, email, social links (if found).

Rules:
- Write in a professional yet approachable tone.
- Use Markdown headings, bullet points, and bold text for readability.
- Do NOT invent facts — only use information present in the provided text.
- Keep it concise but comprehensive (aim for 400-800 words).
- Output ONLY the brochure Markdown — no preamble or commentary.\
"""

_SUMMARY_PROMPT = """\
Summarize the following website content section. Preserve all key facts, \
services, products, statistics, and contact information. Be concise.\

Content:
{text}\
"""

_FINAL_BROCHURE_PROMPT = """\
Using the following summarized website content, create the professional brochure.

Content:
{text}\
"""


def _get_llm() -> ChatGoogleGenerativeAI:
    """Instantiate the Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.7,
        max_retries=2,
    )


def _extract_text(response) -> str:
    """Extract text from LLM response, handling both string and list formats."""
    content = response.content
    
    # If content is a string, return it directly
    if isinstance(content, str):
        return content
    
    # If content is a list (Gemini 3 format), extract text from parts
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])
            elif isinstance(part, str):
                text_parts.append(part)
        return ''.join(text_parts)
    
    # Fallback: convert to string
    return str(content)


def generate_brochure(cleaned_text: str) -> str:
    """Generate a Markdown brochure from cleaned website text.

    If the text fits within one chunk, it is sent directly. Otherwise a
    map-reduce approach is used: each chunk is summarised first, then the
    summaries are combined into the final brochure.
    """
    llm = _get_llm()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
    )

    chunks = splitter.split_text(cleaned_text)
    logger.info("Split content into %d chunk(s)", len(chunks))

    if len(chunks) <= 1:
        # Single chunk — generate directly
        text_block = chunks[0] if chunks else cleaned_text
        messages = [
            ("system", _BROCHURE_SYSTEM_PROMPT),
            ("human", _FINAL_BROCHURE_PROMPT.format(text=text_block)),
        ]
        response = llm.invoke(messages)
        return _extract_text(response)

    # Map phase: summarise each chunk
    summaries: list[str] = []
    for i, chunk in enumerate(chunks):
        logger.info("Summarising chunk %d/%d", i + 1, len(chunks))
        messages = [
            ("system", "You are a helpful assistant that summarizes text accurately."),
            ("human", _SUMMARY_PROMPT.format(text=chunk)),
        ]
        resp = llm.invoke(messages)
        summaries.append(_extract_text(resp))

    # Reduce phase: combine summaries into brochure
    combined_summary = "\n\n---\n\n".join(summaries)
    messages = [
        ("system", _BROCHURE_SYSTEM_PROMPT),
        ("human", _FINAL_BROCHURE_PROMPT.format(text=combined_summary)),
    ]
    response = llm.invoke(messages)
    return _extract_text(response)
