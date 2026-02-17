# P5 Research: Interactive Canvas

**Research Date:** February 16, 2026
**Researcher:** AI Agent Team
**Purpose:** Technical research for the Toledot Interactive Canvas -- a visual timeline and exploration surface that displays church history eras alongside the chat interface, enabling users to navigate eras visually and initiate contextual conversations

---

## Table of Contents

1. [Feature Overview](#1-feature-overview)
2. [Existing Codebase Audit](#2-existing-codebase-audit)
3. [Architecture Decisions](#3-architecture-decisions)
4. [Library Evaluation & Selection](#4-library-evaluation--selection)
5. [Backend: Data Model Changes](#5-backend-data-model-changes)
6. [Backend: API Endpoint Design](#6-backend-api-endpoint-design)
7. [Frontend: Component Architecture](#7-frontend-component-architecture)
8. [Frontend: Interactive Timeline Design](#8-frontend-interactive-timeline-design)
9. [Chat Integration](#9-chat-integration)
10. [Accessibility](#10-accessibility)
11. [Performance Considerations](#11-performance-considerations)
12. [Licensing Summary](#12-licensing-summary)
13. [Architecture Decision Summary](#13-architecture-decision-summary)
14. [Implementation Checklist](#14-implementation-checklist)

---

## 1. Feature Overview

### What Is the Interactive Canvas?

The Interactive Canvas is a visual timeline and exploration surface that sits alongside the existing chat interface. It replaces the static era list/card layout with a rich, animated, interactive visualization of church history eras. Users can:

1. **See eras visually** -- proportionally scaled timeline blocks spanning from 30 AD to the present
2. **Click eras to explore** -- expanding an era reveals its key events and key figures inline
3. **See key events, figures, and councils** -- each era block surfaces its nested data with smooth animations
4. **Integrate with chat** -- clicking an era can create or filter a chat session scoped to that era, bridging exploration and AI conversation

### Why Not Konva.js?

The ARCHITECTURE.md currently lists Konva.js for the Canvas feature. After analysis, Konva.js is **rejected** for the following reasons:

| Factor | Konva.js | Recommended Approach |
|--------|----------|---------------------|
| Complexity | Full 2D canvas engine with custom event system, node tree, layers | Overkill for a timeline with ~6 eras and ~50 events |
| Accessibility | Canvas elements are invisible to screen readers; requires manual ARIA labeling of every drawn element | Native HTML/SVG elements are inherently accessible |
| Text rendering | Poor text wrapping, no native markdown, manual font measurement | HTML `<p>`, `<h3>` render text natively |
| Responsiveness | Manual resize handling, no CSS media queries | Tailwind CSS responsive classes work out of the box |
| Bundle size | ~150KB minified for `react-konva` + `konva` | Zero additional bundle for HTML/CSS approach; ~15KB for `motion` |
| SEO / SSR | Canvas content is invisible to crawlers | HTML content is indexable |
| Learning curve | Custom API for shapes, groups, transforms | Standard React component model |

**Decision:** Build the Interactive Canvas as a **React component tree with Tailwind CSS styling, SVG for the timeline spine, and Motion (framer-motion) for animations**. This approach is simpler, more accessible, more performant, and more maintainable.

---

## 2. Existing Codebase Audit

### 2.1 Backend: Era Models (Already Complete)

The eras app (`backend/apps/eras/models.py`) already has all the data models needed:

```python
class Era(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)  # null = "present"
    description = models.TextField()
    summary = models.TextField(blank=True)
    color = models.CharField(max_length=7)  # Hex color
    order = models.PositiveIntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True)

class KeyEvent(models.Model):
    era = models.ForeignKey(Era, related_name="key_events")
    year = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

class KeyFigure(models.Model):
    era = models.ForeignKey(Era, related_name="key_figures")
    name = models.CharField(max_length=255)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
```

**Seed data** (from `seed_eras.py`) provides six eras with 8-10 key events and 6-8 key figures each:
- Early Church (30-325)
- Nicene & Post-Nicene (325-590)
- Medieval (590-1517)
- Reformation (1517-1648)
- Post-Reformation (1648-1900)
- Contemporary (1900-present)

### 2.2 Backend: Existing API Endpoints

The eras app already provides:

| Endpoint | Method | Serializer | Notes |
|----------|--------|------------|-------|
| `GET /api/eras/` | List | `EraListSerializer` | Returns id, name, slug, start_year, end_year, color, summary, order (no nested events/figures) |
| `GET /api/eras/{slug}/` | Retrieve | `EraDetailSerializer` | Returns all fields + nested key_events and key_figures |
| `GET /api/eras/timeline/` | Custom action | `EraDetailSerializer` | Returns ALL eras with nested events and figures |

The `/api/eras/timeline/` endpoint is **already designed for timeline visualization** and returns the full dataset needed for the Interactive Canvas in a single request. This is a good foundation.

### 2.3 Frontend: Existing Era Components

| Component | Path | Purpose |
|-----------|------|---------|
| `Timeline` | `src/components/eras/Timeline.tsx` | Horizontal bar timeline with proportional era widths. Click to select. |
| `EraCard` | `src/components/eras/EraCard.tsx` | Card with name, year range, summary. Click navigates to `/eras/{slug}`. |
| `KeyEventTimeline` | `src/components/eras/KeyEventTimeline.tsx` | Vertical dot-and-line timeline of events within an era. |
| `KeyFigureCard` | `src/components/eras/KeyFigureCard.tsx` | Card showing figure name, years, title, description. |
| `ErasPage` | `src/pages/ErasPage.tsx` | Full page: horizontal Timeline + detail panel + era cards grid. |
| `EraDetailPage` | `src/pages/EraDetailPage.tsx` | Full page: hero + events + figures + prev/next navigation. |

### 2.4 Frontend: Existing Chat Components

| Component | Path | Purpose |
|-----------|------|---------|
| `ChatPage` | `src/pages/ChatPage.tsx` | Full chat layout with sidebar + message area |
| `ChatSidebar` | `src/components/chat/ChatSidebar.tsx` | Session list with new/delete/switch |
| `MessageList` | `src/components/chat/MessageList.tsx` | Renders conversation messages |
| `ChatInput` | `src/components/chat/ChatInput.tsx` | Input with send/cancel |
| `MessageBubble` | `src/components/chat/MessageBubble.tsx` | Individual message rendering |

### 2.5 Frontend: Existing Stores

| Store | Path | Key State |
|-------|------|-----------|
| `eraStore` | `src/stores/eraStore.ts` | `eras`, `selectedEra`, `isLoading`, `fetchEras()`, `fetchEra()`, `selectEra()` |
| `chatStore` | `src/stores/chatStore.ts` | `sessions`, `activeSessionId`, `messages`, `isStreaming`, `createSession(eraId?)`, `sendMessage()` |

The chat store's `createSession` already accepts an optional `eraId` parameter, which means the era-to-chat integration point already exists at the store level.

### 2.6 Frontend: Existing Packages

Already installed (from `package.json`):
- React 19.2, React DOM 19.2
- TypeScript 5.9
- Vite 7.3
- Tailwind CSS 4.1 + `@tailwindcss/vite`
- `tailwindcss-animate` (for Tailwind CSS animation utilities)
- `zustand` 5.0 (state management)
- `lucide-react` (icons)
- `react-router-dom` 7.13
- `axios` (HTTP client)
- `clsx` + `tailwind-merge` (class utilities via `cn()`)
- `class-variance-authority` (CVA for variant-based component styling)
- `react-markdown` + `remark-gfm` (markdown rendering)

### 2.7 Frontend: API Client

The `services/api.ts` file provides:
- `fetchEras()` -- calls `GET /api/eras/` and maps snake_case to camelCase
- `fetchEra(slug)` -- calls `GET /api/eras/{slug}/` with full detail

There is currently no function that calls the `/api/eras/timeline/` endpoint. This needs to be added.

### 2.8 Frontend: TypeScript Types

From `src/types/index.ts`:
```typescript
export type Era = {
  id: number;
  name: string;
  slug: string;
  startYear: number;
  endYear: number | null;
  description: string;
  summary: string;
  color: string;
  order: number;
  keyEvents?: KeyEvent[];
  keyFigures?: KeyFigure[];
};

export type KeyEvent = {
  id: number;
  year: number;
  title: string;
  description: string;
};

export type KeyFigure = {
  id: number;
  name: string;
  birthYear: number | null;
  deathYear: number | null;
  title: string;
  description: string;
};
```

These types are sufficient for the Interactive Canvas. No type changes are needed.

---

## 3. Architecture Decisions

### 3.1 Page Architecture: Dedicated Canvas Page vs. Chat Integration

**Decision: Build a new `/canvas` page that combines the timeline with a chat panel.**

The Canvas page will be a split-panel layout:
- **Left panel (or top on mobile):** Interactive visual timeline of all eras
- **Right panel (or bottom on mobile):** Chat interface scoped to the selected era

This approach is chosen over modifying the existing `/eras` or `/chat` pages because:
1. The existing `/eras` page serves a different UX purpose (browsable reference)
2. The existing `/chat` page has a sidebar + messages layout that should remain standalone
3. A dedicated `/canvas` page can optimize its layout for the combined experience
4. Users have a clear mental model: "Canvas = explore visually + chat"

The existing `/eras` and `/chat` pages remain unchanged.

### 3.2 Timeline Visualization: HTML/CSS vs. SVG vs. Canvas

**Decision: Hybrid HTML + SVG approach.**

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Era blocks | HTML `<div>` + Tailwind | Clickable, responsive, accessible blocks with text content |
| Timeline spine | SVG `<line>` + `<circle>` | Thin connecting line with year markers between era blocks |
| Animations | Motion (`motion/react`) | Entry animations, expand/collapse, hover effects |
| Layout | CSS Grid + Flexbox | Responsive arrangement of era blocks |

**Why not pure SVG?** SVG is excellent for lines, shapes, and connectors, but poor for reflowing text, responsive layout, and interactive content. Text in SVG requires manual positioning and does not wrap. HTML handles text, interaction, and responsiveness natively.

**Why not HTML Canvas (`<canvas>`)?** Same reasons as rejecting Konva.js: accessibility, text rendering, responsiveness.

### 3.3 Timeline Layout: Horizontal vs. Vertical

**Decision: Vertical timeline (primary) with horizontal overview bar.**

Rationale:
- Vertical timelines accommodate variable-length content per era (events, figures) without horizontal overflow
- The existing `Timeline` component already provides a horizontal overview bar
- Vertical scrolling is the natural interaction model on both desktop and mobile
- The vertical layout leaves horizontal space for the chat panel on desktop

Layout structure:
```
Desktop (>= 1024px):
┌──────────────────────────────────────────────────┐
│  TopNav                                          │
├──────────┬─────────────────┬─────────────────────┤
│ SideNav  │ Timeline Panel  │ Chat Panel          │
│          │ (scrollable)    │ (messages + input)   │
│          │                 │                      │
│          │ [Horizontal bar]│ [Message list]       │
│          │ [Era blocks...] │ [Chat input]         │
│          │                 │                      │
└──────────┴─────────────────┴─────────────────────┘

Tablet (768px - 1023px):
┌──────────────────────────────────────────────────┐
│  TopNav                                          │
├──────────────────────────────────────────────────┤
│ Timeline Panel (top half, scrollable)            │
├──────────────────────────────────────────────────┤
│ Chat Panel (bottom half, collapsible)            │
└──────────────────────────────────────────────────┘

Mobile (< 768px):
┌──────────────────────────────────────────────────┐
│  TopNav                                          │
├──────────────────────────────────────────────────┤
│ Timeline Panel (full screen, scrollable)         │
│ [Floating "Chat about this era" button]          │
├──────────────────────────────────────────────────┤
│  BottomNav                                       │
└──────────────────────────────────────────────────┘
```

On mobile, tapping "Chat about this era" opens a bottom sheet or navigates to `/chat` with the era pre-selected.

### 3.4 State Management

**Decision: Extend the existing `eraStore` with canvas-specific state, rather than creating a new store.**

The `eraStore` already manages `eras`, `selectedEra`, and fetch methods. For the canvas, we add:
- `expandedEraId: number | null` -- which era block is expanded to show events/figures
- `timelineData: Era[] | null` -- cached result from the `/api/eras/timeline/` endpoint (includes nested events/figures)
- `fetchTimeline()` -- calls the timeline endpoint

The chat integration uses the existing `chatStore.createSession(eraId)`.

---

## 4. Library Evaluation & Selection

### 4.1 Animation Library: Motion (formerly Framer Motion)

**Package:** `motion`
**License:** MIT
**npm:** https://www.npmjs.com/package/motion
**GitHub:** https://github.com/motiondivision/motion
**Weekly Downloads:** ~18 million
**React 19 Compatibility:** Yes (requires React 18.2+)
**TypeScript Support:** Full, built-in definitions

**Why Motion?**

Motion (the successor to framer-motion) provides:
- `motion.div` wrapper for declarative animations
- `AnimatePresence` for mount/unmount transitions (expanding/collapsing era details)
- `layoutId` for shared layout animations (smooth transitions between timeline states)
- Spring physics for natural-feeling interactions
- `whileHover`, `whileTap` gesture handlers
- `useInView` hook for scroll-triggered animations (animating era blocks as they scroll into view)
- GPU-accelerated transforms (translate, scale, opacity)
- Tree-shakable: only import what you use (~15KB for typical usage)

**What we use it for:**
1. Era block expand/collapse animation (`AnimatePresence` + `motion.div` with `layout`)
2. Key event/figure entry animations (staggered fade-in when era expands)
3. Hover effects on timeline elements (scale, glow)
4. Scroll-triggered entrance animations for era blocks
5. Timeline horizontal bar selection indicator animation

**Installation:**
```bash
npm install motion
```

**Usage pattern:**
```tsx
import { motion, AnimatePresence } from "motion/react";

function EraBlock({ era, isExpanded, onToggle }) {
  return (
    <motion.div
      layout
      onClick={onToggle}
      className="rounded-lg border bg-card p-6 cursor-pointer"
      whileHover={{ scale: 1.01 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <h3>{era.name}</h3>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Key events and figures */}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
```

### 4.2 Considered and Rejected Libraries

#### react-chrono (Rejected)

**Package:** `react-chrono`
**License:** MIT
**Weekly Downloads:** ~12,000

**Why rejected:**
- Opinionated visual style that would require extensive CSS overriding to match Toledot's design system
- Uses Vanilla Extract CSS (a CSS-in-JS approach), which conflicts with the project's Tailwind CSS v4 approach
- Limited customization of individual timeline items beyond what the API exposes
- No built-in chat integration hooks
- Adds ~80KB to the bundle for features we would not use (slideshow, search, media playback)
- The project's existing `Timeline`, `KeyEventTimeline`, and `KeyFigureCard` components already handle the core rendering; we need animation and layout, not a replacement component library

**Building custom components with Motion animations is more appropriate** given that the project already has well-structured era components and a clear design system.

#### Pure CSS Animations (Rejected as Sole Approach)

**Why rejected as sole approach:**
- CSS `@keyframes` and `transition` handle simple hover/enter effects well, but cannot handle:
  - Dynamic height animations (`height: auto` is not animatable in CSS)
  - Staggered child animations based on data index
  - Mount/unmount transitions (CSS has no `AnimatePresence` equivalent)
  - Layout animations when elements reflow
- Tailwind CSS v4 with `tailwindcss-animate` covers basic transitions, but Motion fills the gaps for complex interactive behaviors

**Decision: Use Tailwind CSS transitions for simple states (hover color, border changes) and Motion for complex animations (expand/collapse, staggered entry, layout shifts).**

#### No Additional Timeline Library

The existing components (`Timeline.tsx`, `KeyEventTimeline.tsx`, `KeyFigureCard.tsx`, `EraCard.tsx`) provide sufficient building blocks. The P5 feature enhances them with:
1. Animation wrappers (Motion)
2. A new layout (split-panel canvas page)
3. Chat integration (click-to-chat)
4. An enhanced vertical timeline layout

No third-party timeline library is needed.

---

## 5. Backend: Data Model Changes

### 5.1 Assessment: No Model Changes Required

The existing `Era`, `KeyEvent`, and `KeyFigure` models contain all the fields needed for the Interactive Canvas:

- Era color, start/end years, name, summary, description -- all present
- KeyEvent year, title, description -- all present
- KeyFigure name, birth/death years, title, description -- all present

The seed data provides rich content for all six eras.

### 5.2 Optional Future Enhancement: Council Model

For a future iteration, a `Council` model could be added to distinguish ecumenical councils from general events. However, councils are currently stored as `KeyEvent` records (e.g., "Council of Nicaea", "Council of Chalcedon"), which is sufficient for P5.

### 5.3 Optional Future Enhancement: Era Icon/Image

The `Era.image_url` field exists but is currently empty in the seed data. Populating this field with representative images (e.g., a cross for Early Church, a cathedral for Medieval) would enhance the visual canvas. This is a data task, not a model change.

---

## 6. Backend: API Endpoint Design

### 6.1 Assessment: No New Endpoints Required

The existing `/api/eras/timeline/` endpoint returns exactly what the Interactive Canvas needs:

```json
[
  {
    "id": 1,
    "name": "Early Church",
    "slug": "early-church",
    "start_year": 30,
    "end_year": 325,
    "description": "The apostolic age...",
    "summary": "The apostolic age, characterized by...",
    "color": "#C2410C",
    "order": 1,
    "image_url": "",
    "created_at": "2026-02-16T...",
    "key_events": [
      { "id": 1, "year": 30, "title": "Pentecost", "description": "...", "order": 1 },
      ...
    ],
    "key_figures": [
      { "id": 1, "name": "Apostle Paul", "birth_year": 5, "death_year": 67, "title": "Apostle to the Gentiles", "description": "...", "order": 1 },
      ...
    ]
  },
  ...
]
```

This single request provides all six eras with their nested events and figures. The response is small (~15-20KB JSON) and cacheable.

### 6.2 Performance Optimization: Cache the Timeline Endpoint

The timeline data changes rarely (only when eras/events/figures are edited in admin). Adding HTTP caching reduces redundant database queries:

```python
# backend/apps/eras/views.py (enhancement)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class EraViewSet(viewsets.ReadOnlyModelViewSet):
    ...

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @action(detail=False, methods=["get"])
    def timeline(self, request):
        eras = self.get_queryset()
        serializer = EraDetailSerializer(eras, many=True)
        return Response(serializer.data)
```

### 6.3 Optional Future Enhancement: Era Statistics Endpoint

A future endpoint could return era content statistics for display on the canvas:

```
GET /api/eras/{slug}/stats/
{
  "content_count": 42,
  "chat_session_count": 15,
  "quiz_count": 8
}
```

This is not needed for P5 MVP but could enhance the canvas with "42 resources available" badges.

---

## 7. Frontend: Component Architecture

### 7.1 New Components

```
src/
├── pages/
│   └── CanvasPage.tsx              # New: split-panel layout
├── components/
│   └── canvas/                     # New: canvas-specific components
│       ├── CanvasTimeline.tsx       # Vertical timeline with animated era blocks
│       ├── CanvasEraBlock.tsx       # Single era block (expandable)
│       ├── CanvasOverviewBar.tsx    # Horizontal mini-timeline for quick navigation
│       ├── CanvasEventList.tsx      # Animated list of key events within expanded era
│       ├── CanvasFigureList.tsx     # Animated list of key figures within expanded era
│       ├── CanvasChatPanel.tsx      # Embedded chat panel for canvas page
│       └── CanvasEmptyState.tsx     # Welcome/instruction state when no era selected
├── stores/
│   └── eraStore.ts                 # Extended with canvas state (timelineData, expandedEraId)
└── services/
    └── api.ts                      # Add fetchTimeline() function
```

### 7.2 Component Tree

```
CanvasPage
├── CanvasOverviewBar               # Horizontal bar at top, shows all 6 eras
│   └── [era buttons]               # Click scrolls to era in timeline, activates era
│
├── SplitPanel (responsive)
│   ├── CanvasTimeline (left/top)   # Scrollable vertical timeline
│   │   ├── CanvasEraBlock (era 1)
│   │   │   ├── Era header (name, years, color badge)
│   │   │   ├── Era summary
│   │   │   └── AnimatePresence
│   │   │       ├── CanvasEventList (when expanded)
│   │   │       │   └── [event items with staggered animation]
│   │   │       └── CanvasFigureList (when expanded)
│   │   │           └── [figure cards with staggered animation]
│   │   ├── SVG connector line
│   │   ├── CanvasEraBlock (era 2)
│   │   │   └── ...
│   │   └── ...
│   │
│   └── CanvasChatPanel (right/bottom)
│       ├── Era context header (shows selected era name + color)
│       ├── MessageList (reused from chat)
│       ├── ChatInput (reused from chat)
│       └── CanvasEmptyState (when no era selected)
│           └── "Select an era to start chatting"
│
└── Mobile: FloatingChatButton
    └── "Chat about {era.name}" (opens bottom sheet or navigates to /chat?era=slug)
```

### 7.3 Component Specifications

#### CanvasPage.tsx

The top-level page component. Registered at `/canvas` in the router.

```tsx
// Responsibilities:
// 1. Fetch timeline data on mount (via eraStore.fetchTimeline())
// 2. Render responsive split-panel layout
// 3. Manage the relationship between selected era and chat session

export function CanvasPage() {
  // Uses eraStore for timeline data and selected era
  // Uses chatStore for chat session management
  // On era selection: creates/switches to a chat session for that era
  // Responsive: lg+ shows side-by-side, md shows stacked, sm shows timeline only
}
```

#### CanvasOverviewBar.tsx

A thin horizontal bar at the top of the timeline panel showing all eras as proportional colored segments. This is an enhanced version of the existing `Timeline` component, adapted for the canvas context.

```tsx
// Responsibilities:
// 1. Render proportional colored bar segments for each era
// 2. Highlight the currently selected/expanded era
// 3. On click: scroll to that era in the vertical timeline and select it
// 4. Sticky positioning at top of timeline panel

type CanvasOverviewBarProps = {
  eras: Era[];
  selectedEraId: number | null;
  onEraClick: (era: Era) => void;
};
```

#### CanvasEraBlock.tsx

The main interactive element. Each era is a card-like block that expands to show events and figures.

```tsx
// Responsibilities:
// 1. Render era name, year range, summary, and color accent
// 2. Click to expand/collapse (toggle expandedEraId in store)
// 3. When expanded: render CanvasEventList + CanvasFigureList with animations
// 4. Show "Chat about this era" action button
// 5. Use motion.div for layout animation on expand/collapse

type CanvasEraBlockProps = {
  era: Era;
  isExpanded: boolean;
  isSelected: boolean;  // selected for chat
  onToggle: () => void;
  onChatClick: () => void;
  blockRef: React.RefObject<HTMLDivElement>;  // for scroll-to functionality
};
```

#### CanvasEventList.tsx

Renders key events inside an expanded era block with staggered entry animation.

```tsx
// Responsibilities:
// 1. Render events as a vertical dot-timeline (similar to existing KeyEventTimeline)
// 2. Staggered fade-in animation using motion.div with delay based on index
// 3. Each event shows year badge + title + description

type CanvasEventListProps = {
  events: KeyEvent[];
  accentColor: string;
};
```

#### CanvasFigureList.tsx

Renders key figures inside an expanded era block with staggered entry animation.

```tsx
// Responsibilities:
// 1. Render figures as compact cards (similar to existing KeyFigureCard)
// 2. Staggered fade-in animation
// 3. Each card shows name, years, title, description

type CanvasFigureListProps = {
  figures: KeyFigure[];
  accentColor: string;
};
```

#### CanvasChatPanel.tsx

An embedded chat panel that reuses existing chat components but is scoped to the selected era.

```tsx
// Responsibilities:
// 1. Show era context header with name and color
// 2. Reuse MessageList and ChatInput components from the chat feature
// 3. When era changes: create a new chat session scoped to that era
// 4. Show empty state when no era is selected

type CanvasChatPanelProps = {
  selectedEra: Era | null;
};
```

---

## 8. Frontend: Interactive Timeline Design

### 8.1 Visual Design Specification

The vertical timeline consists of:

1. **SVG spine line** -- a thin vertical line connecting all era blocks
2. **Era blocks** -- cards positioned along the spine, alternating left/right on desktop (or all on one side)
3. **Year markers** -- small circles on the spine at era boundaries with year labels
4. **Color accents** -- each era's color is used for its border-top, year badge, and event dots

```
                    ┌─ Year Marker: 30 AD
                    │
     ┌──────────────┤   ← SVG spine line
     │ Early Church │
     │ 30-325 AD    │   ← Era block (collapsed)
     │ Summary...   │
     │ [Explore] [Chat] │
     └──────────────┤
                    │
                    ├─ Year Marker: 325 AD
                    │
     ┌──────────────┤
     │ Nicene &     │   ← Era block (expanded)
     │ Post-Nicene  │
     │ 325-590 AD   │
     │ Summary...   │
     │              │
     │ KEY EVENTS   │   ← Animated expansion
     │ ● 325 Nicaea │
     │ ● 381 Const. │
     │ ● 397 Carth. │
     │              │
     │ KEY FIGURES   │
     │ ┌─ Athanasius│
     │ ├─ Augustine │
     │ └─ Basil     │
     │              │
     │ [Chat about this era] │
     └──────────────┤
                    │
                    ├─ Year Marker: 590 AD
                    │
                   ...
```

### 8.2 Animation Specifications

| Animation | Trigger | Motion Config | Duration |
|-----------|---------|--------------|----------|
| Era block entrance | Scroll into view | `initial={{ opacity: 0, y: 30 }}` `animate={{ opacity: 1, y: 0 }}` | 0.5s, spring |
| Era block hover | Mouse enter | `whileHover={{ scale: 1.01, boxShadow: "..." }}` | 0.2s |
| Era expand/collapse | Click | `layout` + `AnimatePresence` with `height: "auto"` | 0.3s, spring |
| Event list stagger | Era expands | `variants` with `staggerChildren: 0.05` | 0.05s per item |
| Figure list stagger | Era expands | `variants` with `staggerChildren: 0.07` | 0.07s per item |
| Overview bar highlight | Era selected | `layoutId="era-highlight"` on indicator | 0.3s, spring |
| Year marker pulse | Era selected | `scale: [1, 1.3, 1]` keyframe loop | 1s, repeat |

### 8.3 Responsive Behavior

| Breakpoint | Timeline Layout | Chat Panel | Overview Bar |
|------------|----------------|------------|--------------|
| >= 1024px (lg) | Left 55% of page | Right 45% of page | Sticky top of timeline panel |
| 768-1023px (md) | Top 50% of page | Bottom 50%, collapsible | Sticky top |
| < 768px (sm) | Full width, scrollable | Hidden (floating "Chat" button) | Sticky top, compact |

### 8.4 Scroll-to-Era Functionality

When a user clicks an era in the overview bar, the vertical timeline should scroll smoothly to that era block:

```tsx
// Using refs and scrollIntoView
const eraRefs = useRef<Map<number, HTMLDivElement>>(new Map());

function scrollToEra(eraId: number) {
  const element = eraRefs.current.get(eraId);
  element?.scrollIntoView({ behavior: "smooth", block: "start" });
}
```

---

## 9. Chat Integration

### 9.1 Era-to-Chat Flow

When a user clicks "Chat about this era" on a canvas era block:

1. **Check if a session for this era exists** in `chatStore.sessions`
2. **If yes:** activate that session (`chatStore.setActiveSession(sessionId)`)
3. **If no:** create a new session scoped to the era (`chatStore.createSession(eraId)`)
4. **Focus the chat input** so the user can immediately type

The existing `chatStore.createSession(eraId)` already supports this:

```typescript
// From chatStore.ts (existing code)
createSession: async (eraId?: string | null) => {
  const session = await createChatSession(eraId);
  set((state) => ({
    sessions: [session, ...state.sessions],
    activeSessionId: session.id,
    messages: [],
  }));
  return session;
},
```

And `createChatSession` sends the era FK to the backend:

```typescript
// From chatApi.ts (existing code)
export async function createChatSession(eraId?: string | null): Promise<ChatSession> {
  const response = await api.post("/chat/sessions/", { era: eraId || null });
  return mapSession(response.data);
}
```

The backend `ChatSession.era` FK then scopes RAG retrieval to that era's content tags via the `retrieve_relevant_chunks` function in `chat/services.py`.

### 9.2 Chat Context Display

The `CanvasChatPanel` should display the active era context:

```tsx
function CanvasChatPanel({ selectedEra }: { selectedEra: Era | null }) {
  return (
    <div className="flex h-full flex-col">
      {selectedEra && (
        <div
          className="flex items-center gap-3 border-b px-4 py-3"
          style={{ borderBottomColor: selectedEra.color }}
        >
          <div
            className="h-3 w-3 rounded-full"
            style={{ backgroundColor: selectedEra.color }}
          />
          <div>
            <p className="text-sm font-semibold">{selectedEra.name}</p>
            <p className="text-xs text-muted-foreground">
              {selectedEra.startYear}--{selectedEra.endYear ?? "present"}
            </p>
          </div>
        </div>
      )}
      {/* Reuse existing MessageList and ChatInput */}
    </div>
  );
}
```

### 9.3 Bidirectional Navigation

The integration should also support navigating from chat to canvas:
- When viewing a chat session that has an `eraId`, a small "View on timeline" link in the chat header navigates to `/canvas` and expands that era
- This can be implemented via URL query parameters: `/canvas?era=early-church`

---

## 10. Accessibility

### 10.1 ARIA Roles and Labels

| Element | ARIA | Notes |
|---------|------|-------|
| Overview bar | `role="tablist"` with `role="tab"` per era | Eras function as tab-like navigation |
| Era blocks | `role="region"` with `aria-label="{era.name}"` | Landmark for each era section |
| Expand/collapse toggle | `aria-expanded="true/false"` | Communicates expanded state |
| Events list | `role="list"` with `role="listitem"` | Semantic list |
| Chat panel | `role="complementary"` with `aria-label="Chat"` | Sidebar landmark |

### 10.2 Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Move between era blocks |
| Enter / Space | Toggle expand/collapse on focused era block |
| Arrow Up/Down | Move between eras in the overview bar |
| Escape | Collapse expanded era |

### 10.3 Motion Preferences

Respect `prefers-reduced-motion`:

```tsx
import { useReducedMotion } from "motion/react";

function CanvasEraBlock({ era, ... }: CanvasEraBlockProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={shouldReduceMotion ? {} : { opacity: 1, y: 0 }}
      // Falls back to instant transitions when reduced motion is preferred
    >
      ...
    </motion.div>
  );
}
```

### 10.4 Color Contrast

Each era's color is used as an accent, not for text. All text uses the theme's `--foreground` or `--muted-foreground` CSS custom properties, ensuring WCAG AA contrast ratios regardless of era color.

---

## 11. Performance Considerations

### 11.1 Data Loading Strategy

**Single request on mount:** The `/api/eras/timeline/` endpoint returns all six eras with their events and figures. This is approximately 15-20KB of JSON, which loads in a single request.

**Caching:** The `eraStore.timelineData` state caches the response. Subsequent visits to `/canvas` skip the network request if data is already loaded. The backend `cache_page(60 * 15)` decorator caches the response at the HTTP level.

### 11.2 Animation Performance

Motion uses GPU-accelerated CSS transforms (`translate`, `scale`, `opacity`) by default. Layout animations that trigger reflow (`height: auto`) are handled via Motion's FLIP technique, which measures the before/after layout and animates the transform.

**Rules for smooth animations:**
- Never animate `width`, `height`, `top`, `left` directly (use `transform` via Motion)
- Use `will-change: transform` on frequently animated elements (Motion handles this automatically)
- Stagger animations: do not animate all 50+ events simultaneously; limit to the 8-10 events in the expanded era

### 11.3 Bundle Size Impact

| Package | Gzipped Size | Tree-shakable |
|---------|-------------|---------------|
| `motion` (typical usage) | ~15KB | Yes -- only imports used features |

The total bundle impact is minimal. The project already includes `tailwindcss-animate` (~2KB), `react-markdown` (~12KB), and `lucide-react` (icons loaded on demand).

### 11.4 Virtualization

With only 6 eras and ~50 total events/figures, virtualization is not needed. All elements can render in the DOM without performance issues. If the dataset grows significantly in the future, `react-window` or `@tanstack/virtual` could be added.

---

## 12. Licensing Summary

### New npm Dependencies

| Package | License | npm | Bundle Size (gzip) |
|---------|---------|-----|-------------------|
| `motion` | MIT | https://www.npmjs.com/package/motion | ~15KB |

### Existing Dependencies (No Changes)

All existing dependencies remain unchanged. The project already has all required packages for the chat panel integration:
- `react` (MIT)
- `react-dom` (MIT)
- `react-router-dom` (MIT)
- `zustand` (MIT)
- `axios` (MIT)
- `tailwindcss` (MIT)
- `@tailwindcss/vite` (MIT)
- `tailwindcss-animate` (MIT)
- `lucide-react` (ISC)
- `clsx` (MIT)
- `tailwind-merge` (MIT)
- `class-variance-authority` (Apache-2.0)
- `react-markdown` (MIT)
- `remark-gfm` (MIT)
- `@microsoft/fetch-event-source` (MIT)

### No New Python Dependencies

The backend requires no new packages. The existing `djangorestframework`, `django`, and PostgreSQL stack handle all API needs.

---

## 13. Architecture Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Canvas approach | HTML/CSS/SVG + React | Accessible, responsive, native text; avoids `<canvas>` element limitations |
| Rejected: Konva.js | HTML/CSS/SVG replaces it | Konva.js is overkill; poor accessibility, text rendering, and responsiveness |
| Rejected: react-chrono | Custom components | Existing era components + Motion animations provide a better fit; react-chrono's styling conflicts with Tailwind |
| Animation library | Motion (`motion/react`) | MIT license, 18M weekly downloads, React 19 compatible, tree-shakable, spring physics |
| Timeline orientation | Vertical (primary) + horizontal overview bar | Vertical accommodates variable-length content; horizontal bar provides navigation |
| Page architecture | New `/canvas` route | Keeps existing `/eras` and `/chat` pages intact; dedicated UX for visual exploration + chat |
| Chat integration | Reuse existing chat components + `chatStore` | `createSession(eraId)` already exists; chat panel embeds `MessageList` + `ChatInput` |
| State management | Extend `eraStore` | Timeline data is era data; no need for a separate store |
| Backend changes | None (models) + optional cache (views) | Existing `/api/eras/timeline/` endpoint already returns all needed data |
| New frontend components | 7 new components in `src/components/canvas/` | Clear separation from existing era components; canvas-specific layout and behavior |
| Responsiveness | Three tiers (lg, md, sm) | Side-by-side on desktop, stacked on tablet, timeline-only on mobile with chat button |
| Accessibility | ARIA roles, keyboard nav, reduced motion | HTML approach inherently accessible; Motion respects `prefers-reduced-motion` |

### Data Flow

```
User opens /canvas
    |
    v
CanvasPage mounts
    |-- eraStore.fetchTimeline()
    |       |
    |       v
    |   GET /api/eras/timeline/
    |       |
    |       v
    |   6 eras with events + figures (cached 15min)
    |       |
    |       v
    |   eraStore.timelineData = response
    |
    v
CanvasOverviewBar + CanvasTimeline render
    |
    v
User clicks "Early Church" era block
    |-- eraStore.expandedEraId = 1
    |-- CanvasEraBlock expands (Motion AnimatePresence)
    |-- CanvasEventList + CanvasFigureList animate in (staggered)
    |
    v
User clicks "Chat about this era"
    |-- chatStore.createSession(eraId=1)
    |       |
    |       v
    |   POST /api/chat/sessions/ { era: 1 }
    |       |
    |       v
    |   New ChatSession created (era FK = Early Church)
    |
    v
CanvasChatPanel activates
    |-- Shows era context header ("Early Church, 30-325 AD")
    |-- MessageList + ChatInput rendered
    |-- User types message
    |       |
    |       v
    |   chatStore.sendMessage(content)
    |       |
    |       v
    |   POST /api/chat/stream/ (SSE)
    |       |-- RAG retrieval scoped to era via ContentItemTag
    |       |-- Claude generates response with era context
    |       |
    |       v
    |   Streaming response displayed in CanvasChatPanel
```

---

## 14. Implementation Checklist

### Backend

- [ ] Add `@method_decorator(cache_page(60 * 15))` to `EraViewSet.timeline()` action for HTTP-level caching
- [ ] Verify `/api/eras/timeline/` returns complete data with `key_events` and `key_figures` nested (already implemented)
- [ ] Populate `Era.image_url` field in seed data with representative images (optional, enhances canvas)

### Frontend: Packages

- [ ] Install `motion`: `npm install motion`

### Frontend: API Layer

- [ ] Add `fetchTimeline()` function to `src/services/api.ts` that calls `GET /api/eras/timeline/` and maps response

### Frontend: State Management

- [ ] Extend `eraStore.ts` with `timelineData`, `expandedEraId`, `fetchTimeline()`, `toggleExpanded(eraId)` actions

### Frontend: Routing

- [ ] Add `/canvas` route to `App.tsx` inside the protected `AppShell` layout
- [ ] Add "Canvas" nav item to `SideNav.tsx` and `BottomNav.tsx` (using a suitable Lucide icon like `Map` or `Layers`)

### Frontend: Components

- [ ] Create `src/components/canvas/CanvasOverviewBar.tsx` -- horizontal era bar with selection indicator
- [ ] Create `src/components/canvas/CanvasTimeline.tsx` -- vertical scrollable timeline container
- [ ] Create `src/components/canvas/CanvasEraBlock.tsx` -- expandable era card with Motion animations
- [ ] Create `src/components/canvas/CanvasEventList.tsx` -- staggered animated event list
- [ ] Create `src/components/canvas/CanvasFigureList.tsx` -- staggered animated figure list
- [ ] Create `src/components/canvas/CanvasChatPanel.tsx` -- embedded chat panel with era context
- [ ] Create `src/components/canvas/CanvasEmptyState.tsx` -- welcome/instruction state
- [ ] Create `src/pages/CanvasPage.tsx` -- top-level page with split-panel layout

### Frontend: Chat Integration

- [ ] In `CanvasChatPanel`, detect if a chat session exists for the selected era and switch to it, or create a new one
- [ ] Add era context header to `CanvasChatPanel` showing selected era name and color
- [ ] Reuse `MessageList` and `ChatInput` from existing chat components

### Frontend: Responsive Design

- [ ] Implement three-tier responsive layout (lg side-by-side, md stacked, sm timeline-only)
- [ ] Add floating "Chat" button on mobile that opens bottom sheet or navigates to `/chat?era={slug}`

### Frontend: Accessibility

- [ ] Add ARIA roles (`tablist`/`tab` on overview bar, `region` on era blocks, `aria-expanded` on toggles)
- [ ] Implement keyboard navigation (Tab, Enter/Space, Arrow keys, Escape)
- [ ] Test with `prefers-reduced-motion` media query (Motion's `useReducedMotion` hook)

### Testing

- [ ] Unit test `CanvasEraBlock` expand/collapse behavior
- [ ] Unit test `CanvasOverviewBar` era selection
- [ ] Unit test chat integration (era -> session creation flow)
- [ ] Unit test responsive layout changes via `useMediaQuery`
- [ ] Integration test: full flow from era click to chat message

---

**End of Research Document**
**Prepared by:** AI Research Agent Team
**Date:** February 16, 2026
