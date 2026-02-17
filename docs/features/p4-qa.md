# P4: AI Chat Agent - QA Review Report

**PR:** #5 (`feature/ai-chat`)
**Reviewer:** QA Engineer
**Date:** 2026-02-16
**Verdict:** CHANGES NEEDED

---

## Summary

The P4 AI Chat Agent implementation is well-structured overall, with solid model design, proper authentication enforcement across all endpoints, good test coverage for models/serializers/views, and a clean frontend component hierarchy. However, there are several issues that need attention before merging -- two critical bugs, a handful of warnings, and various informational notes.

---

## Critical Findings

### C-1: `chat_stream` view is a sync function wrapping an async generator -- broken under WSGI, fragile under ASGI

**File:** `/home/sukim/dev/church_history/backend/apps/chat/views.py` (lines 92-164)

The `chat_stream` view is decorated with `@api_view(["POST"])`, which is a **synchronous** DRF decorator. Inside it, `event_stream()` is defined as an `async def` generator that calls `stream_chat_response` (itself `async def`). The `StreamingHttpResponse` receives this async generator.

**Problem:** Under WSGI (gunicorn with sync workers), Django cannot consume an async generator from a sync view. Under ASGI (uvicorn), Django 5.x can handle `StreamingHttpResponse` with an async iterator, but `@api_view` wraps the view in synchronous DRF machinery (authentication, parsing, content negotiation). This means:

1. DRF's `@api_view` wraps the view as a sync `APIView.dispatch` call, even when running under ASGI.
2. The async generator `event_stream()` is passed to `StreamingHttpResponse`, which Django 5.x ASGI can consume -- but only because Django's ASGI handler detects async iterators on `StreamingHttpResponse` and handles them specially.
3. **However**, the sync DRF view runs authentication and throttle checks synchronously within an async context, which can cause issues with Django's ORM (e.g., the `ChatSession.objects.select_related("era").get(...)` call on line 121 is a synchronous ORM operation running inside what might be an async event loop thread).

**Risk:** This setup works in development but can produce `SynchronousOnlyOperation` errors under ASGI in production, or silently fail under WSGI.

**Recommendation:** Either:
- (a) Convert to a proper async view (remove `@api_view`, write a raw `async def chat_stream(request)` and handle auth/parsing manually or use `adrf`), or
- (b) Verify this exact pattern is tested under uvicorn with ASGI and document that WSGI is not supported for this endpoint.

### C-2: `extract_citations` uses overly broad `[source:]` matching

**File:** `/home/sukim/dev/church_history/backend/apps/chat/services.py` (lines 316-318)

```python
source_notation_used = "[source:" in response_lower
if title_referenced or source_notation_used:
    citations.append(...)
```

If the AI response contains `[Source: anything]` anywhere, **every** provided chunk's content item gets added as a citation, regardless of whether that specific item was referenced. The check `"[source:" in response_lower` is global to the entire response, not specific to the current chunk's title. This means if the AI cites Source A with `[Source: A]`, Sources B, C, D, E, F from the retrieved chunks will all be incorrectly included as citations.

**Recommendation:** Parse `[Source: ...]` notations to extract the referenced title, then match each chunk against the extracted title list. For example:

```python
import re
source_refs = re.findall(r'\[source:\s*([^\]]+)\]', response_lower)
source_notation_match = any(
    item.title.lower() in ref for ref in source_refs
)
```

---

## Warnings

### W-1: `build_messages` fetches history synchronously inside an async pipeline

**File:** `/home/sukim/dev/church_history/backend/apps/chat/services.py` (line 206)

The call is correctly wrapped:
```python
messages = await sync_to_async(build_messages)(session, message_text, context)
```

This is correct. `build_messages` contains synchronous ORM queries (`session.messages.filter(...).order_by(...)`, plus iteration via `list(history[:20])`). Wrapping the entire function in `sync_to_async` is the right approach and evaluates the queryset within the sync context.

**Verdict:** The `sync_to_async` usage here is **correct**. No issue.

### W-2: `retrieve_relevant_chunks` wrapped correctly but `build_context` is not wrapped

**File:** `/home/sukim/dev/church_history/backend/apps/chat/services.py` (line 196)

```python
context = build_context(chunks, era=era)
```

`build_context` does **not** perform any ORM queries -- it only accesses `chunk.content_item` (already fetched via `select_related` in `retrieve_relevant_chunks`), `era.name`, `era.start_year`, `era.end_year`, `era.description`, `item.title`, `item.author`, `item.source.name`. These are all attribute accesses on already-loaded model instances, so no additional DB queries are triggered.

**Verdict:** No wrapping needed. This is **correct** as-is.

### W-3: `session_id` sent as string from frontend but backend expects integer

**File:** `/home/sukim/dev/church_history/frontend/src/services/chatApi.ts` (line 84)

```typescript
body: JSON.stringify({ session_id: sessionId, message }),
```

`sessionId` is typed as `string` (from `ChatSession.id` which is `String(data.id)`). The backend `ChatStreamSerializer` defines `session_id = serializers.IntegerField()`. DRF's `IntegerField` will coerce string `"1"` to integer `1` during validation, so this works in practice.

**Verdict:** Works but is fragile. Consider sending `parseInt(sessionId, 10)` to be explicit, or change the serializer to accept string IDs.

### W-4: `fetchSessions` assumes paginated response but `ChatSessionViewSet` may not paginate

**File:** `/home/sukim/dev/church_history/frontend/src/services/chatApi.ts` (line 39)

```typescript
return response.data.results.map(mapSession);
```

The `ChatSessionViewSet` inherits from `ModelViewSet`, which uses the global `DEFAULT_PAGINATION_CLASS` (`PageNumberPagination` with `PAGE_SIZE=20`). So the response **will** be `{count, next, previous, results: [...]}`. This is correct.

However, if a user has more than 20 sessions, only the first 20 will be shown. The frontend does not handle pagination (no "load more" or infinite scroll). This is a usability issue but not a bug for the initial release.

**Verdict:** Acceptable for MVP. Document as a known limitation.

### W-5: `pagination_class = None` on `ChatMessageListView` is intentional and correct

**File:** `/home/sukim/dev/church_history/backend/apps/chat/views.py` (line 77)

The code comment explains: "Pagination is disabled since chat UIs need the full conversation history." The frontend `fetchMessages` (line 60) correctly reads `response.data.map(mapMessage)` (a plain array, not `response.data.results`). The backend test (line 688) confirms `len(response.data) == 2` (direct array).

**Verdict:** Correct. The `pagination_class = None` is intentional and consistent between frontend and backend.

### W-6: Potential N+1 query in `ChatSessionSerializer.get_message_count`

**File:** `/home/sukim/dev/church_history/backend/apps/chat/serializers.py` (line 80)

```python
def get_message_count(self, obj):
    return obj.messages.count()
```

The viewset does `prefetch_related("messages")` (views.py line 57), which prefetches all messages. However, `.count()` on a prefetched queryset in Django does **not** use the prefetch cache -- it issues a new `SELECT COUNT(*)` query. This results in N+1 queries when listing sessions.

**Recommendation:** Use `len(obj.messages.all())` to leverage the prefetch cache, or better yet, use `annotate(message_count=Count("messages"))` in the viewset queryset and access it as a plain attribute.

### W-7: SSE stream does not send a final `event: done` field -- relies on JSON payload

**File:** `/home/sukim/dev/church_history/backend/apps/chat/views.py` (line 150)

The SSE format is `data: {"type": "delta|done|error", ...}\n\n`. This works with `@microsoft/fetch-event-source`, but standard SSE clients (e.g., `EventSource` API) would see all events as generic `message` events. Since the frontend uses `fetchEventSource` which handles this fine, this is acceptable. However, using named events (`event: delta\ndata: ...\n\n`) would be more standards-compliant.

**Verdict:** Acceptable for current implementation. Consider named events for future SSE standardization.

### W-8: `mapCitation` handles both `source_name` and `source` field names

**File:** `/home/sukim/dev/church_history/frontend/src/services/chatApi.ts` (lines 30-34)

```typescript
source: (data.source_name as string) || (data.source as string) || "",
```

This defensive coding handles two different response shapes:
- From the `MessageCitationSerializer` (REST response): field is `source_name`
- From the SSE `done` event (services.py line 287): field is `source`

This is correct and necessary because the SSE `done` payload uses `"source"` while the serializer uses `"source_name"`. This divergence is a minor API inconsistency.

**Recommendation:** Align the SSE payload key to `source_name` (matching the serializer) for consistency:
```python
# services.py line 287
"source_name": c.get("source_name", ""),  # instead of "source"
```

### W-9: `cancelStream` does not clean up the partial streaming message

**File:** `/home/sukim/dev/church_history/frontend/src/stores/chatStore.ts` (lines 189-195)

When the user cancels a stream, `streamingContent` is cleared and `isStreaming` is set to false. However, the optimistic user message (added at line 138) remains in the `messages` array. The assistant never gets to respond, so the conversation shows a user message with no reply. The user message was also already saved server-side (services.py line 199-203), creating a persisted user message with no corresponding assistant message.

**Verdict:** This is expected behavior for cancellation, but the UX could be confusing. The user message has already been sent to the backend and saved before the stream even begins, so it cannot be "unsent." Consider showing a subtle "(cancelled)" indicator or allowing the user to retry.

---

## Informational Notes

### I-1: `is_archived` field exists but is not used in the frontend

**File:** `/home/sukim/dev/church_history/backend/apps/chat/models.py` (line 33)

The `is_archived` field is defined on `ChatSession` and is patchable via the API (tested in test_chat.py line 662-671), but the frontend sidebar does not filter out archived sessions and does not provide a UI to archive. The `ChatSession` type definition in `types/index.ts` also does not include `isArchived`.

**Verdict:** Feature stub for future use. No issue.

### I-2: `mapSession` drops several fields from the API response

**File:** `/home/sukim/dev/church_history/frontend/src/services/chatApi.ts` (lines 6-14)

The `mapSession` function only maps `id`, `title`, `eraId`, `createdAt`, `updatedAt`. The API also returns `era_name`, `is_archived`, `total_input_tokens`, `total_output_tokens`, `message_count`. These are intentionally dropped as they're not needed in the current frontend.

**Verdict:** Acceptable. The TypeScript type correctly represents only what's used.

### I-3: `ChatSession.eraId` is typed as `string | null` but `Era.id` is `number`

**File:** `/home/sukim/dev/church_history/frontend/src/types/index.ts` (line 50 vs line 10)

The `ChatSession.eraId` is `string | null` (because `mapSession` converts with `String(data.era)`), while `Era.id` is `number`. When `createChatSession` sends `era: eraId || null`, it sends a string ID. The backend serializer accepts this because DRF's FK field coerces strings to integers.

**Verdict:** Works but type mismatch between `ChatSession.eraId` (string) and `Era.id` (number) could cause confusion if comparing them. Consider keeping `eraId` as `number | null`.

### I-4: `build_context` truncates era description to 500 characters

**File:** `/home/sukim/dev/church_history/backend/apps/chat/services.py` (line 117)

```python
context_parts.append(f"Description: {era.description[:500]}")
```

This is a reasonable safeguard against very long descriptions consuming too much context window.

**Verdict:** Good practice.

### I-5: History limit of 20 messages in `build_messages`

**File:** `/home/sukim/dev/church_history/backend/apps/chat/services.py` (line 149)

```python
history = list(history[:20])
```

This limits conversation history to the last 20 messages sent to Claude. Combined with the user's new message, this means up to 21 messages in the API call. This is a reasonable context window management strategy.

**Verdict:** Good practice. The limit is tested in `test_build_messages_limits_history`.

### I-6: `max_tokens=2048` is hardcoded

**File:** `/home/sukim/dev/church_history/backend/apps/chat/services.py` (line 220)

The max tokens for Claude responses is hardcoded at 2048. Consider making this configurable via settings for flexibility.

**Verdict:** Acceptable for initial release. Consider adding `ANTHROPIC_MAX_TOKENS` setting.

### I-7: Anthropic API key defaults to empty string

**File:** `/home/sukim/dev/church_history/backend/config/settings/base.py` (line 229)

```python
ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
```

If the environment variable is not set, the Anthropic client will be initialized with an empty API key, which will fail at request time. The `anthropic.AsyncAnthropic` constructor accepts empty strings without raising. The error will only surface when `client.messages.stream()` is called, resulting in an `anthropic.APIConnectionError` or `anthropic.AuthenticationError`.

**Verdict:** The error handling in `stream_chat_response` (lines 233-244) catches `APIConnectionError` and `APIStatusError`, which would cover this case. Consider adding a startup check or logging a warning if the key is empty.

### I-8: Model `claude-haiku-4-5-20251001` is the default

**File:** `/home/sukim/dev/church_history/backend/config/settings/base.py` (line 230)

```python
ANTHROPIC_MODEL = config("ANTHROPIC_MODEL", default="claude-haiku-4-5-20251001")
```

Using Haiku as the default is a good cost-conscious choice for a teaching assistant.

**Verdict:** Good default.

### I-9: `MessageBubble` source citation links have no empty-URL guard

**File:** `/home/sukim/dev/church_history/frontend/src/components/chat/MessageBubble.tsx` (lines 114-129)

Citation links render `<a href={source.url}>` even when `source.url` is an empty string (which is possible since `MessageCitation.url` has `blank=True` and the `mapCitation` function defaults to `""`). An `<a href="">` link navigates to the current page.

**Recommendation:** Conditionally render the link as a `<span>` when `source.url` is empty:
```tsx
{source.url ? (
  <a href={source.url} target="_blank" rel="noopener noreferrer" ...>
    ...
  </a>
) : (
  <span ...>{source.title}</span>
)}
```

### I-10: `ChatSidebar` session items use `role="button"` with keyboard support -- good accessibility

**File:** `/home/sukim/dev/church_history/frontend/src/components/chat/ChatSidebar.tsx` (lines 84-102)

The session items correctly use `role="button"`, `tabIndex={0}`, and handle both `Enter` and `Space` key events. The delete buttons have proper `aria-label` attributes. This is solid accessible markup.

**Verdict:** Good accessibility implementation.

### I-11: Frontend tests do not test the `MessageList` component directly

**File:** `/home/sukim/dev/church_history/frontend/src/test/chat.test.tsx`

There are no dedicated tests for `MessageList`. It is indirectly tested through `ChatPage` tests, but the streaming UI (thinking dots, pulsing cursor, Markdown rendering during streaming) is not covered.

**Recommendation:** Add tests for `MessageList` covering: loading state, empty state, streaming indicator, auto-scroll behavior.

### I-12: Backend tests for `chat_stream` only test error paths, not the happy path SSE response

**File:** `/home/sukim/dev/church_history/backend/tests/test_chat.py` (class `TestChatStreamAPI`)

The stream endpoint tests verify 401, 400, and 404 responses, plus cross-user 404. There is no test that verifies the happy path (200 with streaming response). This is understandable since testing async SSE streaming with DRF's `APIClient` is non-trivial, but it leaves the most important code path untested.

**Recommendation:** Add an integration test using Django's `ASGIRequestFactory` or an async test client to verify the full streaming pipeline, even if it requires mocking the Anthropic API.

### I-13: `@microsoft/fetch-event-source` version 2.0.1 -- MIT licensed

**File:** `/home/sukim/dev/church_history/frontend/package.json` (line 18)

The package is MIT licensed. All other dependencies in the frontend and backend are MIT, Apache-2.0, or BSD licensed.

**Verdict:** No license issues.

### I-14: No secrets found in code

All API keys and secrets are loaded from environment variables via `python-decouple`. No hardcoded credentials were found in any reviewed file.

**Verdict:** Security is properly handled.

---

## Migration Review

**File:** `/home/sukim/dev/church_history/backend/apps/chat/migrations/0001_initial.py`

The migration correctly creates all three models (`ChatSession`, `ChatMessage`, `MessageCitation`) with:
- All fields matching the model definitions
- Correct FK relationships and `on_delete` behaviors (`CASCADE` for session/message, `SET_NULL` for era)
- All four indexes matching the model `Meta.indexes`
- Correct `ordering` options
- Proper dependencies on `accounts`, `eras`, and `content` apps

**Verdict:** Migration matches models. No issues.

---

## Dependency Review

| Package | License | Notes |
|---------|---------|-------|
| anthropic>=0.40.0 | MIT | Claude API client |
| @microsoft/fetch-event-source ^2.0.1 | MIT | SSE client |
| uvicorn[standard]>=0.32.0 | BSD-3-Clause | ASGI server for streaming |
| All other backend deps | MIT/Apache-2.0/BSD | Previously reviewed |
| All other frontend deps | MIT | Previously reviewed |

**Verdict:** All dependencies have permissive licenses. No issues.

---

## Security Review

| Check | Status | Notes |
|-------|--------|-------|
| Authentication on all endpoints | PASS | All views require `IsAuthenticated` |
| Session ownership enforcement | PASS | ViewSet filters by user; stream endpoint verifies ownership |
| No secrets in code | PASS | All via environment variables |
| CSRF on SSE endpoint | PASS | Frontend sends `X-CSRFToken` header |
| Rate limiting on AI endpoint | PASS | 30/hour sustained, 5/min burst |
| Input validation | PASS | `ChatStreamSerializer` validates session_id and message |
| Message length limit | PASS | `max_length=10000` on message field |
| XSS via Markdown | PASS | `react-markdown` does not render raw HTML by default |
| External links | PASS | All `target="_blank"` links have `rel="noopener noreferrer"` |

**Verdict:** Security posture is solid.

---

## Summary of Required Changes

| ID | Severity | Summary |
|----|----------|---------|
| C-1 | Critical | `chat_stream` is a sync DRF view wrapping an async generator -- verify/document ASGI-only support or refactor to a proper async view |
| C-2 | Critical | `extract_citations` adds all chunks as citations when any `[Source: ...]` notation appears anywhere in the response |
| W-6 | Warning | N+1 query in `get_message_count` -- use annotation or `len()` on prefetched queryset |
| W-8 | Warning | SSE `done` payload uses `"source"` key while serializer uses `"source_name"` -- inconsistent API shape |
| W-9 | Warning | Cancelled streams leave orphaned user messages with no assistant response |
| I-9 | Info | Citation links with empty URLs navigate to current page |
| I-11 | Info | No direct tests for `MessageList` component |
| I-12 | Info | No happy-path integration test for SSE streaming endpoint |

**Overall Verdict: CHANGES NEEDED** -- C-1 and C-2 should be resolved before merge.
