"""RAG service module for the Toledot AI chat assistant.

Provides retrieval-augmented generation (RAG) functionality using pgvector
for semantic search and the Anthropic Claude API for response generation.
"""

import json
import logging

import anthropic
from asgiref.sync import sync_to_async
from django.conf import settings
from pgvector.django import CosineDistance

from apps.content.models import ContentChunk
from apps.eras.models import Era

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Toledot, a church history teaching assistant grounded in the Reformed \
theological tradition. Your purpose is to help users learn about and understand the history of \
the Christian church from the apostolic era to the present day.

Guidelines:
- Answer using the provided source materials whenever possible.
- Cite sources using [Source: title] notation when referencing specific content.
- Frame discussions within the Reformed tradition while fairly representing other traditions \
and perspectives.
- Be honest when the provided sources are insufficient to fully answer a question.
- Provide historically accurate information with appropriate nuance and context.
- When discussing theological disagreements, present the Reformed position clearly while \
acknowledging other views charitably.
- Keep responses educational, clear, and accessible to learners at various levels.
- If no relevant sources are provided, answer from your general knowledge but note that \
the response is not grounded in the provided materials.
"""


def get_query_embedding(text: str):
    """Generate an embedding vector for a query string.

    Uses the lazy-loaded sentence-transformers model from the content app
    to ensure consistency between search and chat embeddings.

    Args:
        text: The query text to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    from apps.content.views import _get_query_embedding

    return _get_query_embedding(text)


def retrieve_relevant_chunks(query_text, era=None, top_k=6, min_score=0.3):
    """Retrieve relevant content chunks using pgvector cosine similarity search.

    Performs a semantic search against the content chunk embeddings to find
    the most relevant passages for the given query.

    Args:
        query_text: The user's question or search query.
        era: Optional Era instance to filter results by era tag.
        top_k: Maximum number of chunks to retrieve.
        min_score: Minimum cosine similarity score (0.0-1.0) to include.

    Returns:
        A list of ContentChunk instances ordered by relevance.
    """
    query_embedding = get_query_embedding(query_text)

    chunks = (
        ContentChunk.objects.select_related("content_item__source")
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")
    )

    if era:
        chunks = chunks.filter(
            content_item__tags__slug=era.slug,
            content_item__tags__tag_type="era",
        )

    chunks = chunks[:top_k]

    results = []
    for chunk in chunks:
        similarity = 1 - chunk.distance
        if similarity >= min_score:
            results.append(chunk)

    return results


def build_context(chunks, era=None):
    """Build a context string from retrieved chunks for prompt augmentation.

    Constructs a formatted text block containing era information and
    source content that will be injected into the user message for RAG.

    Args:
        chunks: List of ContentChunk instances with related data.
        era: Optional Era instance to include era context.

    Returns:
        A formatted string containing the assembled context.
    """
    context_parts = []

    if era:
        end_year = era.end_year or "present"
        context_parts.append(
            f"Current Era: {era.name} ({era.start_year}-{end_year})"
        )
        context_parts.append(f"Description: {era.description[:500]}")

    for chunk in chunks:
        item = chunk.content_item
        author = item.author or "Unknown"
        context_parts.append(
            f"--- Source: {item.title} by {author} ---"
        )
        context_parts.append(chunk.chunk_text)
        context_parts.append("--- End Source ---")

    return "\n\n".join(context_parts)


def build_messages(session, user_message, context):
    """Build the messages array for the Claude API call.

    Constructs a conversation history from the session's stored messages,
    then appends the current user message augmented with RAG context.

    Args:
        session: The ChatSession instance.
        user_message: The current user message text.
        context: The RAG context string to prepend.

    Returns:
        A list of message dicts suitable for the Claude messages API.
    """
    history = session.messages.filter(
        role__in=["user", "assistant"]
    ).order_by("created_at")

    # Limit to last 20 messages for context window management
    history = list(history[:20])

    messages = []
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    # Add context-augmented user message
    if context:
        augmented_content = (
            f"Relevant sources:\n{context}\n\nUser question: {user_message}"
        )
    else:
        augmented_content = user_message

    messages.append({"role": "user", "content": augmented_content})
    return messages


async def stream_chat_response(session, user_message_text, era=None):
    """Stream a chat response using Claude with RAG context.

    Performs the full RAG pipeline: retrieves relevant chunks, builds context,
    sends the augmented prompt to Claude, streams the response, and persists
    all messages and citations to the database.

    Args:
        session: The ChatSession instance.
        user_message_text: The user's message text.
        era: Optional Era instance to scope the search.

    Yields:
        Dicts with SSE event data:
        - {"type": "delta", "content": "..."} for each text chunk
        - {"type": "done", "message_id": "...", "citations": [...]} on completion
        - {"type": "error", "content": "..."} on failure
    """
    from .models import ChatMessage, MessageCitation

    # Retrieve relevant chunks (sync ORM - must be wrapped for async)
    try:
        chunks = await sync_to_async(retrieve_relevant_chunks)(
            user_message_text, era=era
        )
    except Exception:
        logger.exception("Failed to retrieve chunks for RAG")
        chunks = []

    context = build_context(chunks, era=era)

    # Save user message
    user_msg = await ChatMessage.objects.acreate(
        session=session,
        role=ChatMessage.Role.USER,
        content=user_message_text,
    )

    # Build messages for Claude (sync ORM - must be wrapped for async)
    messages = await sync_to_async(build_messages)(
        session, user_message_text, context
    )

    # Stream response from Claude
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    full_response = ""
    input_tokens = 0
    output_tokens = 0

    try:
        async with client.messages.stream(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                yield {"type": "delta", "content": text}

            # Get final message for token counts
            final_message = await stream.get_final_message()
            input_tokens = final_message.usage.input_tokens
            output_tokens = final_message.usage.output_tokens

    except anthropic.APIConnectionError:
        logger.exception("Failed to connect to Anthropic API")
        yield {"type": "error", "content": "Failed to connect to AI service."}
        return
    except anthropic.RateLimitError:
        logger.exception("Anthropic API rate limit exceeded")
        yield {"type": "error", "content": "AI service rate limit exceeded. Please try again later."}
        return
    except anthropic.APIStatusError as e:
        logger.exception("Anthropic API error: %s", e.message)
        yield {"type": "error", "content": "AI service error. Please try again later."}
        return

    # Save assistant message
    assistant_msg = await ChatMessage.objects.acreate(
        session=session,
        role=ChatMessage.Role.ASSISTANT,
        content=full_response,
        model_used=settings.ANTHROPIC_MODEL,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    # Save retrieved chunks reference
    if chunks:
        await assistant_msg.retrieved_chunks.aset([c.id for c in chunks])

    # Extract and save citations
    citations = extract_citations(full_response, chunks)
    for i, citation in enumerate(citations):
        await MessageCitation.objects.acreate(
            message=assistant_msg,
            content_item=citation["content_item"],
            title=citation["title"],
            url=citation.get("url", ""),
            source_name=citation.get("source_name", ""),
            order=i,
        )

    # Update session token counts
    session.total_input_tokens += input_tokens
    session.total_output_tokens += output_tokens
    await session.asave(
        update_fields=["total_input_tokens", "total_output_tokens", "updated_at"]
    )

    yield {
        "type": "done",
        "message_id": str(assistant_msg.id),
        "citations": [
            {
                "title": c["title"],
                "url": c.get("url", ""),
                "source": c.get("source_name", ""),
            }
            for c in citations
        ],
    }


def extract_citations(response_text, chunks):
    """Extract source citations from the AI response text.

    Matches retrieved chunks against the response to determine which
    sources were actually referenced, either by title mention or
    by [Source: ...] notation.

    Args:
        response_text: The full AI-generated response text.
        chunks: The list of ContentChunk instances that were provided as context.

    Returns:
        A list of dicts with keys: content_item, title, url, source_name.
    """
    citations = []
    seen_items = set()
    response_lower = response_text.lower()

    for chunk in chunks:
        item = chunk.content_item
        if item.id not in seen_items:
            seen_items.add(item.id)
            # Check if this source is referenced in the response
            title_referenced = item.title.lower() in response_lower
            source_notation_used = "[source:" in response_lower
            if title_referenced or source_notation_used:
                citations.append(
                    {
                        "content_item": item,
                        "title": item.title,
                        "url": item.url,
                        "source_name": item.source.name if item.source else "",
                    }
                )

    return citations
