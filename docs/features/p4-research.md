# P4 Research: AI Chat Agent

**Research Date:** February 16, 2026
**Researcher:** AI Agent Team
**Purpose:** Technical research for Toledot AI Chat Agent — a Reformed theology teaching assistant powered by Claude Haiku 4.5 with RAG retrieval over the P2 content pipeline

---

## Table of Contents

1. [LLM Provider & Model Selection](#1-llm-provider--model-selection)
2. [Streaming Architecture](#2-streaming-architecture)
3. [RAG Pipeline Integration](#3-rag-pipeline-integration)
4. [Chat Data Models](#4-chat-data-models)
5. [Frontend Chat UI](#5-frontend-chat-ui)
6. [Rate Limiting](#6-rate-limiting)
7. [Environment Variables & Secrets](#7-environment-variables--secrets)
8. [Licensing Summary](#8-licensing-summary)
9. [Architecture Decision Summary](#9-architecture-decision-summary)

---

## 1. LLM Provider & Model Selection

### Recommendation: Anthropic Claude API with Claude Haiku 4.5

**Model:** `claude-haiku-4-5-20251001`
**SDK:** `anthropic` Python SDK (MIT license)
**PyPI:** [pypi.org/project/anthropic](https://pypi.org/project/anthropic/)
**GitHub:** [github.com/anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python)

**Why Claude Haiku 4.5 for MVP:**

| Factor | Detail |
|--------|--------|
| Cost | Lowest cost in the Claude family — critical for a student-facing educational app |
| Latency | Fastest time-to-first-token; good for streaming UX |
| Context window | 200K tokens — allows full conversation history + injected RAG chunks without truncation |
| Quality | Strong instruction following; well-suited for teaching assistant persona |
| License | MIT SDK — commercially permissive, no copyleft restrictions |

**Why not GPT-4o or Gemini?**
Claude was purpose-built by Anthropic with a focus on helpfulness and accuracy in grounded contexts. Its instruction-following for system prompts (including Reformed theology persona injection) is reliable. The MIT-licensed SDK avoids license friction.

---

### SDK Installation

```bash
pip install anthropic
```

---

### Prompt Caching

Claude supports prompt caching with up to **4 cache breakpoints** per request. For a chat agent that always sends:
1. A static system prompt (Reformed theology teaching assistant persona)
2. Retrieved RAG chunks (semi-static per session topic)
3. Conversation history
4. The current user message

Cache breakpoints should be placed at the end of each stable prefix to minimize re-processing cost:

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},  # Breakpoint 1: static system prompt
        }
    ],
    messages=[
        # Breakpoint 2: injected RAG context (changes per query but stable within a turn)
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": rag_context_block,
                    "cache_control": {"type": "ephemeral"},  # Breakpoint 2: RAG context
                },
                {
                    "type": "text",
                    "text": conversation_history_block,
                    "cache_control": {"type": "ephemeral"},  # Breakpoint 3: history
                },
                {
                    "type": "text",
                    "text": user_message,
                    # Breakpoint 4 reserved for future multi-turn cache
                },
            ],
        }
    ],
)
```

**Cache benefits:**
- System prompt cached after first call — saves ~500 tokens per request
- Conversation history cached per turn — especially valuable in long sessions
- Anthropic charges ~10% of input token cost for cache reads

---

### System Prompt Design

The system prompt establishes the teaching assistant persona and Reformed theological framework:

```python
SYSTEM_PROMPT = """You are a knowledgeable teaching assistant for Toledot, an educational app
focused on church history from a Reformed theological perspective.

Your role:
- Help users understand church history, theology, and the development of Reformed Christianity
- Teach from a Reformed confessional perspective (Westminster Standards, Three Forms of Unity)
- Affirm the five solas: Scripture alone, faith alone, grace alone, Christ alone, glory of God alone
- Ground answers in the provided source materials when available
- Cite sources by name when drawing from them (e.g., "According to Calvin's Institutes...")
- Be honest when a question exceeds the available sources; suggest further study
- Use accessible language while maintaining theological precision

Theological commitments:
- Scripture is the only infallible rule of faith and practice
- Salvation is by grace alone through faith alone in Christ alone
- God's sovereign grace governs all of history, including church history
- The Reformation was a recovery of biblical Christianity, not an innovation

When answering:
1. Prioritize information from the provided context sources
2. Inject the historical era perspective when relevant
3. Acknowledge complexity and honest historical disputes
4. Avoid anachronism (do not project modern categories onto ancient figures)
5. Be warm and pedagogically encouraging

If asked about topics outside church history or Reformed theology, gently redirect to
the app's educational scope.
"""
```

---

## 2. Streaming Architecture

### Overview

Streaming delivers tokens to the user as they are generated, creating a responsive chat experience. The stack is:

- **Backend:** Django async view returning `StreamingHttpResponse` over ASGI (uvicorn)
- **Frontend:** `@microsoft/fetch-event-source` for SSE with POST support

---

### Backend: Django Async StreamingHttpResponse + ASGI

**Why async + ASGI?**

Django's default WSGI server (gunicorn) handles one request per thread. Streaming responses hold a connection open for several seconds. Under load, this exhausts thread pools. ASGI + uvicorn handles this with cooperative I/O — a single worker can stream many responses concurrently.

**ASGI server:** `uvicorn[standard]`
**License:** BSD-3-Clause
**PyPI:** [pypi.org/project/uvicorn](https://pypi.org/project/uvicorn/)

```bash
pip install uvicorn[standard]
```

**Running the ASGI app:**

```bash
# Development
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000

# Production (with gunicorn process manager)
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -w 4
```

**ASGI configuration:**

```python
# config/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
application = get_asgi_application()
```

---

### Backend: Streaming View Implementation

```python
# apps/chat/views.py
import json
import anthropic
from django.http import StreamingHttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from decouple import config

from apps.chat.rag import retrieve_context
from apps.chat.models import ChatSession, ChatMessage
from apps.chat.throttles import ChatBurstThrottle, ChatHourlyThrottle


class ChatStreamView(LoginRequiredMixin, View):
    """Streams Claude responses via SSE (Server-Sent Events)."""

    throttle_classes = [ChatBurstThrottle, ChatHourlyThrottle]

    async def post(self, request, session_id):
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message is required."}, status=400)

        session = await ChatSession.objects.aget(id=session_id, user=request.user)

        # Retrieve RAG context
        retrieved_chunks = await retrieve_context(
            query=user_message,
            era=session.era,
            top_k=6,
            min_score=0.3,
        )

        # Build conversation history from DB
        history = await self._build_history(session)

        return StreamingHttpResponse(
            self._stream_response(session, user_message, history, retrieved_chunks),
            content_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    async def _stream_response(self, session, user_message, history, retrieved_chunks):
        client = anthropic.AsyncAnthropic(api_key=config("ANTHROPIC_API_KEY"))

        rag_context = self._format_rag_context(retrieved_chunks)
        full_user_content = f"{rag_context}\n\n---\n\n{user_message}" if rag_context else user_message

        accumulated_text = ""
        input_tokens = 0
        output_tokens = 0

        async with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=history + [{"role": "user", "content": full_user_content}],
        ) as stream:
            async for text in stream.text_stream:
                accumulated_text += text
                # Emit SSE event
                yield f"data: {json.dumps({'type': 'delta', 'text': text})}\n\n"

            # Final usage from stream
            final_message = await stream.get_final_message()
            input_tokens = final_message.usage.input_tokens
            output_tokens = final_message.usage.output_tokens

        # Persist to DB after streaming completes
        await self._persist_messages(
            session=session,
            user_message=user_message,
            assistant_response=accumulated_text,
            retrieved_chunks=retrieved_chunks,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        # Emit done event with citation data
        citations = self._build_citations(retrieved_chunks)
        yield f"data: {json.dumps({'type': 'done', 'citations': citations})}\n\n"

    def _format_rag_context(self, chunks):
        if not chunks:
            return ""
        parts = ["The following sources are relevant to the user's question:\n"]
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Source {i}] {chunk.title} ({chunk.source_name})\n{chunk.content}\n"
            )
        return "\n".join(parts)

    def _build_citations(self, chunks):
        return [
            {
                "title": c.title,
                "url": c.source_url,
                "source_name": c.source_name,
            }
            for c in chunks
        ]

    async def _build_history(self, session):
        messages = []
        async for msg in ChatMessage.objects.filter(
            session=session
        ).exclude(role="system").order_by("created_at")[:20]:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    async def _persist_messages(
        self, session, user_message, assistant_response,
        retrieved_chunks, input_tokens, output_tokens
    ):
        user_msg = await ChatMessage.objects.acreate(
            session=session,
            role="user",
            content=user_message,
            input_tokens=0,
            output_tokens=0,
        )
        assistant_msg = await ChatMessage.objects.acreate(
            session=session,
            role="assistant",
            content=assistant_response,
            model_used="claude-haiku-4-5-20251001",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        if retrieved_chunks:
            await assistant_msg.retrieved_chunks.aset(retrieved_chunks)

        # Update session token totals
        session.total_input_tokens = (session.total_input_tokens or 0) + input_tokens
        session.total_output_tokens = (session.total_output_tokens or 0) + output_tokens
        await session.asave(update_fields=["total_input_tokens", "total_output_tokens"])
```

---

### Frontend: `@microsoft/fetch-event-source`

**Why not the browser's native `EventSource` API?**

The browser's native `EventSource` only supports `GET` requests. Chat endpoints require `POST` with:
- A JSON body (the user's message)
- A CSRF token header (`X-CSRFToken`)
- Session cookies (for authentication)

`@microsoft/fetch-event-source` is a drop-in SSE client built on `fetch`, supporting `POST`, custom headers, and automatic reconnection.

**Package:** `@microsoft/fetch-event-source`
**License:** MIT
**npm:** [npmjs.com/package/@microsoft/fetch-event-source](https://www.npmjs.com/package/@microsoft/fetch-event-source)
**Weekly Downloads:** ~1.1 million

```bash
npm install @microsoft/fetch-event-source
```

**Usage:**

```tsx
// frontend/src/services/chatStream.ts
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { getCsrfToken } from '@/utils/csrf';

export async function streamChatMessage({
  sessionId,
  message,
  onDelta,
  onDone,
  onError,
  signal,
}: {
  sessionId: string;
  message: string;
  onDelta: (text: string) => void;
  onDone: (citations: Citation[]) => void;
  onError: (err: Error) => void;
  signal: AbortSignal;
}) {
  await fetchEventSource(`/api/chat/sessions/${sessionId}/stream/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    credentials: 'include',  // Send session cookies
    body: JSON.stringify({ message }),
    signal,
    onmessage(event) {
      const data = JSON.parse(event.data);
      if (data.type === 'delta') {
        onDelta(data.text);
      } else if (data.type === 'done') {
        onDone(data.citations ?? []);
      }
    },
    onerror(err) {
      onError(err instanceof Error ? err : new Error(String(err)));
      throw err; // Stops automatic retry
    },
  });
}
```

---

## 3. RAG Pipeline Integration

### Overview

P4 reuses the existing P2 pgvector infrastructure and `all-MiniLM-L6-v2` embeddings with no additional dependencies. The retrieval layer adds **hybrid filtering**: vector similarity + era-based tag filtering via `ContentItemTag`.

---

### Retrieval Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `top_k` | 5–8 | Balances context richness vs. token cost in Claude prompt |
| `min_score` | 0.3 | Cosine similarity floor; below 0.3 is typically off-topic noise |
| Era filter | Optional FK to `Era` model | Scopes retrieval to the session's era when set |
| Distance metric | Cosine similarity (`<=>`) | Standard for `all-MiniLM-L6-v2` embeddings |

---

### RAG Retrieval Implementation

```python
# apps/chat/rag.py
from sentence_transformers import SentenceTransformer
from pgvector.django import CosineDistance
from apps.content.models import ContentChunk, ContentItemTag

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


async def retrieve_context(query: str, era=None, top_k: int = 6, min_score: float = 0.3):
    """
    Hybrid retrieval: vector similarity + optional era-based filtering.
    Returns top_k ContentChunk instances above min_score threshold.
    """
    model = get_embedding_model()
    query_embedding = model.encode(query)

    qs = ContentChunk.objects.annotate(
        similarity=1 - CosineDistance("embedding", query_embedding)
    ).filter(similarity__gte=min_score)

    # Era-based filtering via ContentItemTag join
    if era is not None:
        era_item_ids = ContentItemTag.objects.filter(
            tag__slug=f"era-{era.slug}"
        ).values_list("content_item_id", flat=True)
        qs = qs.filter(content_item_id__in=era_item_ids)

    results = await qs.order_by("-similarity").aslice(0, top_k)
    return list(results)
```

---

### Era Context Injection

When a `ChatSession` has an `era` FK set, the system prompt is augmented with era context before sending to Claude:

```python
def build_era_context(era) -> str:
    if era is None:
        return ""
    return (
        f"The user is currently studying the {era.name} era ({era.date_range}). "
        f"Focus your answers on this period of church history where relevant. "
        f"Key themes for this era: {era.key_themes}."
    )
```

This era context string is appended to the system prompt or prepended to the user message before RAG context injection. Inserting it after the static system prompt (which is cached) keeps the static cache breakpoint intact.

---

### Retrieval Quality Considerations

- **Threshold tuning:** Start with `min_score=0.3`. If answers include off-topic chunks, raise to `0.4`. If answers are too sparse, lower to `0.25`.
- **top_k=6 default:** Six 512-token chunks = ~3,072 tokens of context. With Claude Haiku's 200K context window and a ~500-token system prompt, this leaves ample room for conversation history.
- **Empty results:** If retrieval returns zero chunks above threshold, the system falls back to Claude's pretrained knowledge. The system prompt instructs it to acknowledge this explicitly.

---

## 4. Chat Data Models

### Model Definitions

```python
# apps/chat/models.py
from django.db import models
from django.contrib.auth import get_user_model
from apps.content.models import ContentChunk

User = get_user_model()


class ChatSession(models.Model):
    """
    A single conversation thread. Optionally scoped to an era for focused RAG retrieval.
    Tracks token usage for cost monitoring and usage quotas.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    era = models.ForeignKey(
        "content.Era",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_sessions",
        help_text="If set, RAG retrieval is filtered to this era.",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Auto-generated from first message or user-defined.",
    )
    total_input_tokens = models.PositiveIntegerField(default=0)
    total_output_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.email} — {self.title or 'Untitled'} ({self.created_at.date()})"


class ChatMessage(models.Model):
    """
    A single message within a ChatSession. Stores the role, content, model used,
    token counts, and which content chunks were retrieved for this turn.
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    content = models.TextField()
    model_used = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="e.g. 'claude-haiku-4-5-20251001'. Empty for user messages.",
    )
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    retrieved_chunks = models.ManyToManyField(
        ContentChunk,
        blank=True,
        related_name="cited_in_messages",
        help_text="RAG chunks used to ground this assistant response.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}..."


class MessageCitation(models.Model):
    """
    Denormalized citation record linking an assistant message to a source item.
    Stores title, URL, and source name at the time of generation so citations
    remain accurate even if ContentItem metadata is later updated.
    """
    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, related_name="citations"
    )
    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_citations",
    )
    # Denormalized for citation stability
    title = models.CharField(max_length=500)
    url = models.URLField(blank=True, default="")
    source_name = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Citation: {self.title} (message {self.message_id})"
```

---

### Migration Notes

- `ChatSession.era` uses `SET_NULL` on delete so sessions persist if an `Era` record is removed
- `ChatMessage.retrieved_chunks` M2M is optional — user messages will have an empty set
- `MessageCitation` denormalizes `title`/`url`/`source_name` to protect citation integrity; the FK to `ContentItem` is nullable so citations survive content pruning

---

## 5. Frontend Chat UI

### Component Architecture

```
ChatPage
├── ChatSidebar
│   ├── NewChatButton
│   ├── SessionList (list of ChatSession titles)
│   └── EraFilter (optional era selector)
└── ChatWindow
    ├── EraHeader (shows active era if set)
    ├── MessageList
    │   ├── UserMessage
    │   └── AssistantMessage
    │       ├── ReactMarkdown (renders markdown response)
    │       └── CitationList
    ├── StreamingIndicator (animated dots while isStreaming)
    └── ChatInput
        ├── Textarea (auto-resize)
        ├── SendButton (disabled while streaming)
        └── CancelButton (visible while streaming, triggers AbortController)
```

---

### Markdown Rendering

**Package:** `react-markdown` (MIT)
**npm:** [npmjs.com/package/react-markdown](https://www.npmjs.com/package/react-markdown)

**Plugin:** `remark-gfm` (MIT) — GitHub Flavored Markdown (tables, strikethrough, task lists)
**npm:** [npmjs.com/package/remark-gfm](https://www.npmjs.com/package/remark-gfm)

```bash
npm install react-markdown remark-gfm
```

**AssistantMessage component:**

```tsx
// frontend/src/components/chat/AssistantMessage.tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Citation } from '@/types/chat';

interface Props {
  content: string;
  citations: Citation[];
  isStreaming?: boolean;
}

export function AssistantMessage({ content, citations, isStreaming }: Props) {
  return (
    <div className="assistant-message">
      <div className="message-content prose prose-sm max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
        {isStreaming && <span className="streaming-cursor" aria-hidden>▊</span>}
      </div>

      {citations.length > 0 && !isStreaming && (
        <CitationList citations={citations} />
      )}
    </div>
  );
}
```

---

### Zustand Chat Store

```tsx
// frontend/src/stores/chatStore.ts
import { create } from 'zustand';
import { streamChatMessage } from '@/services/chatStream';
import type { ChatSession, ChatMessage, Citation } from '@/types/chat';

type ChatStore = {
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  abortController: AbortController | null;

  setActiveSession: (id: string) => void;
  sendMessage: (message: string) => Promise<void>;
  cancelStream: () => void;
  appendStreamDelta: (text: string) => void;
  finalizeStream: (citations: Citation[]) => void;
};

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',
  abortController: null,

  setActiveSession: (id) => {
    set({ activeSessionId: id, messages: [], streamingContent: '' });
  },

  sendMessage: async (message) => {
    const { activeSessionId } = get();
    if (!activeSessionId) return;

    // Optimistically add user message
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      citations: [],
      createdAt: new Date().toISOString(),
    };
    set((s) => ({ messages: [...s.messages, userMsg] }));

    // Start streaming
    const controller = new AbortController();
    set({ isStreaming: true, streamingContent: '', abortController: controller });

    try {
      await streamChatMessage({
        sessionId: activeSessionId,
        message,
        onDelta: (text) => get().appendStreamDelta(text),
        onDone: (citations) => get().finalizeStream(citations),
        onError: (err) => {
          if (err.name !== 'AbortError') {
            console.error('Stream error:', err);
          }
          set({ isStreaming: false, streamingContent: '', abortController: null });
        },
        signal: controller.signal,
      });
    } catch {
      set({ isStreaming: false, streamingContent: '', abortController: null });
    }
  },

  cancelStream: () => {
    const { abortController } = get();
    abortController?.abort();
    set({ isStreaming: false, streamingContent: '', abortController: null });
  },

  appendStreamDelta: (text) => {
    set((s) => ({ streamingContent: s.streamingContent + text }));
  },

  finalizeStream: (citations) => {
    const { streamingContent } = get();
    const assistantMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: streamingContent,
      citations,
      createdAt: new Date().toISOString(),
    };
    set((s) => ({
      messages: [...s.messages, assistantMsg],
      isStreaming: false,
      streamingContent: '',
      abortController: null,
    }));
  },
}));
```

---

### ChatInput with AbortController

```tsx
// frontend/src/components/chat/ChatInput.tsx
import { useState, useRef } from 'react';
import { useChatStore } from '@/stores/chatStore';

export function ChatInput() {
  const [input, setInput] = useState('');
  const { isStreaming, sendMessage, cancelStream } = useChatStore();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    setInput('');
    await sendMessage(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about church history..."
        disabled={isStreaming}
        rows={1}
        className="chat-textarea"
      />

      {isStreaming ? (
        <button
          type="button"
          onClick={cancelStream}
          className="cancel-button"
          aria-label="Cancel response"
        >
          Stop
        </button>
      ) : (
        <button
          type="submit"
          disabled={!input.trim()}
          className="send-button"
          aria-label="Send message"
        >
          Send
        </button>
      )}
    </form>
  );
}
```

---

## 6. Rate Limiting

### Strategy: DRF UserRateThrottle with Scoped Rates

Two throttle classes protect the chat endpoint:

| Throttle | Rate | Purpose |
|----------|------|---------|
| `ChatBurstThrottle` | 5/minute | Prevents rapid-fire queries (e.g., accidental double-click loops) |
| `ChatHourlyThrottle` | 30/hour | Limits total AI API spend per user per hour |

**Implementation:**

```python
# apps/chat/throttles.py
from rest_framework.throttling import UserRateThrottle


class ChatBurstThrottle(UserRateThrottle):
    scope = "chat_burst"


class ChatHourlyThrottle(UserRateThrottle):
    scope = "chat_hourly"
```

**Settings:**

```python
# config/settings/base.py

REST_FRAMEWORK = {
    # ... existing settings ...
    "DEFAULT_THROTTLE_CLASSES": [],  # No global throttle; applied per-view
    "DEFAULT_THROTTLE_RATES": {
        "chat_burst": "5/minute",
        "chat_hourly": "30/hour",
    },
}

# Django cache backend for throttle state
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }
}
```

**Applying throttles to the streaming view:**

```python
# apps/chat/views.py (updated)
from apps.chat.throttles import ChatBurstThrottle, ChatHourlyThrottle
from rest_framework.throttling import UserRateThrottle

class ChatStreamView(LoginRequiredMixin, View):
    ...

    def get_throttles(self):
        return [ChatBurstThrottle(), ChatHourlyThrottle()]

    def check_throttles(self, request):
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                self.throttled(request, throttle.wait())
```

**Why Redis/Valkey for throttle cache?**
- The in-process LocMem cache is per-process and does not coordinate across multiple uvicorn workers
- Redis (or its MIT-licensed drop-in Valkey) is already required for Celery (P2 scraping pipeline) and provides a shared, durable counter store

---

## 7. Environment Variables & Secrets

### ANTHROPIC_API_KEY

The API key is the only new secret introduced in P4. It is managed via `python-decouple` (already used throughout the project) and must never be committed to version control.

**Reading the key in code:**

```python
# anywhere in the backend
from decouple import config

ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY")
```

**Local development — `.env` file (never committed):**

```dotenv
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

**`.gitignore` verification:**

```
# .gitignore (should already contain)
.env
*.env
.env.*
```

**Production — environment injection:**

Set `ANTHROPIC_API_KEY` as a secure environment variable in your deployment platform (Railway, Render, Fly.io, AWS ECS task definition, etc.). Never bake it into a Docker image layer.

---

### Full Environment Variable Reference (P4 additions)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic Claude API key |
| `REDIS_URL` | Yes (production) | `redis://127.0.0.1:6379/1` | Redis/Valkey for throttle cache |

---

## 8. Licensing Summary

All new P4 dependencies use commercially permissive licenses. No copyleft (GPL/LGPL/AGPL) dependencies are introduced.

### Python Dependencies

| Package | License | pip install |
|---------|---------|-------------|
| `anthropic` | MIT | `pip install anthropic` |
| `uvicorn[standard]` | BSD-3-Clause | `pip install uvicorn[standard]` |

### npm Dependencies

| Package | License | npm install |
|---------|---------|-------------|
| `@microsoft/fetch-event-source` | MIT | `npm install @microsoft/fetch-event-source` |
| `react-markdown` | MIT | `npm install react-markdown` |
| `remark-gfm` | MIT | `npm install remark-gfm` |

### requirements.txt additions

```txt
# LLM provider
anthropic>=0.40.0  # MIT license

# ASGI server
uvicorn[standard]>=0.30.0  # BSD-3-Clause license
```

### package.json additions

```json
{
  "dependencies": {
    "@microsoft/fetch-event-source": "^2.0.1",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0"
  }
}
```

---

## 9. Architecture Decision Summary

### Key Decisions and Rationale

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM provider | Anthropic Claude API | MIT SDK, strong instruction following, 200K context |
| Model | `claude-haiku-4-5-20251001` | Lowest cost + latency in Claude family; sufficient quality for teaching assistant |
| Prompt caching | 4 cache breakpoints | Reduces input token cost; system prompt and RAG context are primary caches |
| Streaming transport | `StreamingHttpResponse` + ASGI | Django async + uvicorn handles many concurrent SSE streams efficiently |
| SSE client | `@microsoft/fetch-event-source` (MIT) | Only SSE client supporting POST + custom headers (needed for CSRF + session) |
| Embedding reuse | `all-MiniLM-L6-v2` + pgvector | No new infrastructure; reuses P2 pipeline |
| Hybrid retrieval | Vector similarity + era FK filter | Scopes RAG to relevant era when session has era context |
| top_k | 5–8 (default 6) | Balances context richness vs. Claude token budget |
| min_score | 0.3 | Cosine similarity floor eliminates off-topic noise |
| Markdown rendering | `react-markdown` + `remark-gfm` | MIT, standard React ecosystem; supports tables and lists from Claude responses |
| State management | Zustand `chatStore` | Already used in project; streaming state fits naturally in a single store |
| Cancel mechanism | `AbortController` | Native browser API; works with `@microsoft/fetch-event-source` `signal` parameter |
| Rate limiting | DRF `UserRateThrottle` (scoped) | Two-tier: burst (5/min) + hourly (30/hr); backed by Redis |
| Secrets management | `python-decouple` config | Already in project; reads from `.env` locally, environment in production |

---

### Data Flow

```
User Types Message
    │
    ▼
ChatInput (React)
    └── useChatStore.sendMessage()
    │
    ▼
fetchEventSource POST /api/chat/sessions/{id}/stream/
    ├── X-CSRFToken header
    └── credentials: include (session cookies)
    │
    ▼
ChatStreamView (Django async view)
    ├── Throttle check (burst + hourly via Redis)
    ├── retrieve_context()
    │   ├── Embed query → all-MiniLM-L6-v2
    │   └── pgvector cosine search + era filter → top-6 chunks
    └── anthropic.AsyncAnthropic.messages.stream()
        ├── System prompt (cached)
        ├── RAG context block (cached)
        ├── Conversation history (last 20 messages)
        └── User message
    │
    ▼
SSE stream → frontend
    ├── delta events → chatStore.appendStreamDelta()
    │   └── AssistantMessage renders ReactMarkdown in real time
    └── done event → chatStore.finalizeStream(citations)
        └── CitationList rendered below message
    │
    ▼
Post-stream DB persistence
    ├── ChatMessage (user) saved
    ├── ChatMessage (assistant) saved with token counts
    ├── retrieved_chunks M2M set
    └── ChatSession token totals updated
```

---

### Implementation Checklist

**Backend:**
- [ ] Install `anthropic` and `uvicorn[standard]`; add to `requirements.txt`
- [ ] Add `ANTHROPIC_API_KEY` to `.env` (local) and deployment environment
- [ ] Switch from WSGI to ASGI: update `config/asgi.py`, update `Procfile`/`Dockerfile` to use `uvicorn`
- [ ] Create `apps/chat/` app with `models.py`, `views.py`, `rag.py`, `throttles.py`
- [ ] Add `ChatSession`, `ChatMessage`, `MessageCitation` models and run migrations
- [ ] Register `ChatStreamView` at `POST /api/chat/sessions/<id>/stream/`
- [ ] Add `CACHES` pointing to Redis in settings
- [ ] Add `DEFAULT_THROTTLE_RATES` for `chat_burst` and `chat_hourly`

**Frontend:**
- [ ] Install `@microsoft/fetch-event-source`, `react-markdown`, `remark-gfm`
- [ ] Create `chatStore.ts` with streaming state (`isStreaming`, `streamingContent`, `abortController`)
- [ ] Create `chatStream.ts` service using `fetchEventSource` with POST + CSRF header
- [ ] Build `ChatPage` layout with `ChatSidebar` and `ChatWindow`
- [ ] Build `MessageList`, `UserMessage`, `AssistantMessage` (with `ReactMarkdown`)
- [ ] Build `CitationList` component
- [ ] Build `ChatInput` with `AbortController`-based cancel button
- [ ] Handle `isStreaming` disabled state on `SendButton`

**Testing:**
- [ ] Unit test `retrieve_context()` — mock embeddings, verify era filtering
- [ ] Unit test `ChatStreamView` — mock Anthropic client, assert SSE events
- [ ] Unit test throttles — assert 6th burst request returns 429
- [ ] Frontend: test `chatStore` state transitions (idle → streaming → done → idle)
- [ ] Frontend: test cancel flow triggers abort and resets state

---

**End of Research Document**
**Prepared by:** AI Research Agent Team
**Date:** February 16, 2026
