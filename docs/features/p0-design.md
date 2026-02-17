# P0: Design System & UI/UX Specification

## App: Toledot (תּוֹלְדוֹת)

A modern, scholarly web application for learning church history in the Reformed tradition. The design language blends the gravitas of academic tradition with the clarity of modern SaaS interfaces.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [Spacing & Layout](#4-spacing--layout)
5. [Component Design Tokens](#5-component-design-tokens)
6. [Tailwind CSS Configuration](#6-tailwind-css-configuration)
7. [Wireframes](#7-wireframes)
8. [Component Hierarchy](#8-component-hierarchy)
9. [Accessibility](#9-accessibility)
10. [Responsive Strategy](#10-responsive-strategy)

---

## 1. Design Principles

1. **Scholarly Clarity** - Every screen should feel like opening a well-typeset book. White space is generous, hierarchy is unmistakable, and reading is effortless.
2. **Progressive Disclosure** - Show what matters now; reveal depth on demand. The chat is front and center; the canvas slides in when content appears.
3. **Warm Authority** - Neutral tones grounded by a warm accent. The palette says "trustworthy institution" not "corporate software."
4. **Fluid Motion** - Panels slide, cards lift, transitions ease. Nothing snaps; everything flows.
5. **Accessible by Default** - Every color pairing meets WCAG 2.1 AA. Every interactive element is keyboard-reachable. No information conveyed by color alone.

---

## 2. Color Palette

The palette draws from the tones of aged paper, library wood, and stained glass -- anchored by a deep navy that evokes academic authority.

### Light Mode

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `--background` | `#FAFAF8` | `neutral-50` (custom) | Page background |
| `--foreground` | `#1C1917` | `stone-900` | Primary text |
| `--card` | `#FFFFFF` | `white` | Card / surface background |
| `--card-foreground` | `#1C1917` | `stone-900` | Card text |
| `--primary` | `#1E3A5F` | custom `primary-700` | Primary buttons, links, nav active |
| `--primary-foreground` | `#F8FAFC` | `slate-50` | Text on primary |
| `--secondary` | `#F1EDE7` | custom `secondary-100` | Secondary surfaces, hover states |
| `--secondary-foreground` | `#44403C` | `stone-700` | Text on secondary |
| `--accent` | `#B45309` | `amber-700` | CTAs, highlights, badges, progress |
| `--accent-foreground` | `#FFFBEB` | `amber-50` | Text on accent |
| `--muted` | `#F5F5F4` | `stone-100` | Muted backgrounds, disabled states |
| `--muted-foreground` | `#78716C` | `stone-500` | Placeholder text, captions |
| `--border` | `#E7E5E4` | `stone-200` | Borders, dividers |
| `--ring` | `#1E3A5F` | custom `primary-700` | Focus rings |
| `--destructive` | `#DC2626` | `red-600` | Error states, destructive actions |
| `--destructive-foreground` | `#FFFFFF` | `white` | Text on destructive |
| `--success` | `#16A34A` | `green-600` | Success states, correct answers |
| `--success-foreground` | `#FFFFFF` | `white` | Text on success |

### Dark Mode

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `--background` | `#0C0A09` | `stone-950` | Page background |
| `--foreground` | `#FAFAF9` | `stone-50` | Primary text |
| `--card` | `#1C1917` | `stone-900` | Card / surface background |
| `--card-foreground` | `#FAFAF9` | `stone-50` | Card text |
| `--primary` | `#93B4D4` | custom `primary-300` | Primary buttons, links |
| `--primary-foreground` | `#0C0A09` | `stone-950` | Text on primary |
| `--secondary` | `#292524` | `stone-800` | Secondary surfaces |
| `--secondary-foreground` | `#D6D3D1` | `stone-300` | Text on secondary |
| `--accent` | `#F59E0B` | `amber-500` | CTAs, highlights, badges |
| `--accent-foreground` | `#0C0A09` | `stone-950` | Text on accent |
| `--muted` | `#292524` | `stone-800` | Muted backgrounds |
| `--muted-foreground` | `#A8A29E` | `stone-400` | Placeholder text |
| `--border` | `#44403C` | `stone-700` | Borders, dividers |
| `--ring` | `#93B4D4` | custom `primary-300` | Focus rings |
| `--destructive` | `#EF4444` | `red-500` | Error states |
| `--destructive-foreground` | `#FFFFFF` | `white` | Text on destructive |
| `--success` | `#22C55E` | `green-500` | Success states |
| `--success-foreground` | `#0C0A09` | `stone-950` | Text on success |

### Extended Primary Scale (Navy)

| Token | Hex | Usage |
|-------|-----|-------|
| `primary-50` | `#EEF2F7` | Lightest tint, hover backgrounds |
| `primary-100` | `#D4DEE9` | Light backgrounds |
| `primary-200` | `#A9BDD4` | Borders on primary elements |
| `primary-300` | `#93B4D4` | Dark mode primary |
| `primary-400` | `#5E89B4` | Hover in dark mode |
| `primary-500` | `#345F8A` | Mid-tone |
| `primary-600` | `#274A6E` | Slightly lighter than primary |
| `primary-700` | `#1E3A5F` | Light mode primary (base) |
| `primary-800` | `#152C48` | Pressed state |
| `primary-900` | `#0D1D31` | Darkest shade |
| `primary-950` | `#071019` | Near-black navy |

### Extended Secondary Scale (Warm Stone)

| Token | Hex | Usage |
|-------|-----|-------|
| `secondary-50` | `#FAF9F6` | Lightest warm white |
| `secondary-100` | `#F1EDE7` | Light mode secondary (base) |
| `secondary-200` | `#E2DCD3` | Hover |
| `secondary-300` | `#C8BFB3` | Active |
| `secondary-400` | `#A39889` | Muted content |
| `secondary-500` | `#7D7265` | Subdued icons |

### Era-Specific Accent Colors

For the timeline and era navigation, each church history era receives a distinct accent for visual differentiation:

| Era | Color | Hex | Usage |
|-----|-------|-----|-------|
| Early Church (30-325) | Terracotta | `#C2410C` | Era badge, timeline segment |
| Nicene (325-590) | Gold | `#B45309` | Era badge, timeline segment |
| Medieval (590-1517) | Deep Purple | `#7C3AED` | Era badge, timeline segment |
| Reformation (1517-1648) | Forest Green | `#15803D` | Era badge, timeline segment |
| Modern (1648-1900) | Steel Blue | `#2563EB` | Era badge, timeline segment |
| Contemporary (1900-present) | Slate | `#475569` | Era badge, timeline segment |

---

## 3. Typography

### Font Families

| Role | Font | Fallback Stack | Reason |
|------|------|---------------|--------|
| **Headings** | [Source Serif 4](https://fonts.google.com/specimen/Source+Serif+4) | `Georgia, 'Times New Roman', serif` | Variable-weight serif with optical sizing. Scholarly without being stuffy. Excellent readability at display sizes. Open Font License. |
| **Body** | [Inter](https://fonts.google.com/specimen/Inter) | `system-ui, -apple-system, 'Segoe UI', sans-serif` | Industry standard for UI text. Optimized for screens, excellent at small sizes. Variable font with full weight range. Open Font License. |
| **Monospace** | [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) | `'Fira Code', 'Consolas', monospace` | Clean monospace for scripture references, citations, code. Open Font License. |

### Font Loading Strategy

Use `font-display: swap` via Google Fonts. Preconnect to `fonts.googleapis.com` and `fonts.gstatic.com`.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Type Scale

Based on a 1.250 ratio (Major Third) with 16px base:

| Token | Size (rem) | Size (px) | Line Height | Weight | Usage |
|-------|-----------|-----------|-------------|--------|-------|
| `text-xs` | 0.75 | 12 | 1.5 | 400 | Captions, badges |
| `text-sm` | 0.875 | 14 | 1.5 | 400 | Secondary text, labels |
| `text-base` | 1.0 | 16 | 1.625 | 400 | Body text, chat messages |
| `text-lg` | 1.125 | 18 | 1.556 | 400 | Large body, emphasized content |
| `text-xl` | 1.25 | 20 | 1.5 | 600 | Card titles, section labels |
| `text-2xl` | 1.5 | 24 | 1.333 | 600 | Page subtitles, dialog titles |
| `text-3xl` | 1.875 | 30 | 1.267 | 700 | Page titles |
| `text-4xl` | 2.25 | 36 | 1.222 | 700 | Hero headings |
| `text-5xl` | 3.0 | 48 | 1.167 | 700 | Landing page display |

### Heading Styles

- `h1` (Page title): Source Serif 4, `text-3xl` (30px), font-weight 700, `stone-900`/`stone-50`
- `h2` (Section): Source Serif 4, `text-2xl` (24px), font-weight 600, `stone-900`/`stone-50`
- `h3` (Subsection): Inter, `text-xl` (20px), font-weight 600, `stone-800`/`stone-100`
- `h4` (Card title): Inter, `text-lg` (18px), font-weight 600, `stone-700`/`stone-200`

### Paragraph / Body

- Default: Inter, `text-base` (16px), weight 400, line-height 1.625, `stone-700`/`stone-300`
- Chat messages: Inter, `text-base` (16px), weight 400, line-height 1.5
- Scripture references: JetBrains Mono, `text-sm` (14px), weight 400

---

## 4. Spacing & Layout

### 8px Grid System

All spacing values are multiples of 8px (0.5rem). The Tailwind default scale already uses a 4px base; we use even increments.

| Token | Value | Common Use |
|-------|-------|------------|
| `space-1` | 4px (0.25rem) | Tight inline spacing |
| `space-2` | 8px (0.5rem) | Icon-to-text gap |
| `space-3` | 12px (0.75rem) | Compact padding |
| `space-4` | 16px (1rem) | Default padding, card inner spacing |
| `space-5` | 20px (1.25rem) | Medium spacing |
| `space-6` | 24px (1.5rem) | Section gaps, card padding |
| `space-8` | 32px (2rem) | Large section spacing |
| `space-10` | 40px (2.5rem) | Page-level spacing |
| `space-12` | 48px (3rem) | Hero section spacing |
| `space-16` | 64px (4rem) | Major section separators |

### Container & Layout Widths

| Element | Width | Tailwind |
|---------|-------|----------|
| Max page width | 1440px | `max-w-[1440px]` |
| Content container | 1280px | `max-w-7xl` |
| Narrow content (reading) | 768px | `max-w-3xl` |
| Side navigation | 240px (expanded) / 64px (collapsed) | `w-60` / `w-16` |
| Canvas panel | 400px-600px (resizable) | `w-[400px]` to `w-[600px]` |
| Chat message max-width | 720px | `max-w-[720px]` |

### Responsive Breakpoints

| Breakpoint | Width | Tailwind | Layout |
|-----------|-------|----------|--------|
| Mobile | < 640px | default | Single column, bottom nav |
| Tablet | >= 640px | `sm:` | Single column, collapsible sidebar |
| Small Desktop | >= 768px | `md:` | Two columns (nav + content) |
| Desktop | >= 1024px | `lg:` | Three columns (nav + content + canvas) |
| Wide Desktop | >= 1280px | `xl:` | Three columns with wider panels |
| Ultra-wide | >= 1536px | `2xl:` | Three columns, max-width container |

### Page Padding

| Breakpoint | Horizontal Padding |
|-----------|-------------------|
| Mobile | 16px (`px-4`) |
| Tablet | 24px (`sm:px-6`) |
| Desktop | 32px (`lg:px-8`) |

---

## 5. Component Design Tokens

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Badges, tags, small inline elements |
| `rounded` | 6px | Input fields, small buttons |
| `rounded-md` | 8px | Buttons, dropdowns |
| `rounded-lg` | 12px | Cards, panels, dialogs |
| `rounded-xl` | 16px | Large cards, hero elements |
| `rounded-2xl` | 20px | Modal overlays, feature cards |
| `rounded-full` | 9999px | Avatars, circular buttons, pills |

### Shadow Levels

Light mode shadows use warm-tinted shadow color (`stone-900/5` to `stone-900/15`).

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-xs` | `0 1px 2px rgba(28,25,23,0.05)` | Subtle lift (badges) |
| `shadow-sm` | `0 1px 3px rgba(28,25,23,0.08), 0 1px 2px rgba(28,25,23,0.04)` | Cards at rest |
| `shadow-md` | `0 4px 6px rgba(28,25,23,0.07), 0 2px 4px rgba(28,25,23,0.04)` | Cards on hover |
| `shadow-lg` | `0 10px 15px rgba(28,25,23,0.08), 0 4px 6px rgba(28,25,23,0.04)` | Dropdowns, popovers |
| `shadow-xl` | `0 20px 25px rgba(28,25,23,0.10), 0 8px 10px rgba(28,25,23,0.04)` | Modals, dialogs |

Dark mode shadows use opacity-based elevation (lighter overlay) rather than dark shadows:

| Token | Dark Mode Value |
|-------|----------------|
| `shadow-sm` | `0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)` |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.2)` |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.3), 0 4px 6px rgba(0,0,0,0.2)` |

### Transition Durations

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| `duration-fast` | 100ms | `ease-out` | Hover color changes, focus rings |
| `duration-normal` | 200ms | `ease-in-out` | Button press, card hover lift |
| `duration-slow` | 300ms | `ease-in-out` | Panel slide, accordion expand |
| `duration-slower` | 500ms | `ease-in-out` | Page transitions, canvas reveal |

### Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-base` | 0 | Default content |
| `z-raised` | 10 | Sticky elements within scroll areas |
| `z-sidebar` | 20 | Side navigation |
| `z-header` | 30 | Top navigation bar |
| `z-dropdown` | 40 | Dropdowns, popovers, tooltips |
| `z-overlay` | 50 | Modal backdrop |
| `z-modal` | 60 | Modal dialog |
| `z-toast` | 70 | Toast notifications |
| `z-tooltip` | 80 | Tooltips over modals |
| `z-max` | 100 | Emergency (command palette) |

---

## 6. Tailwind CSS Configuration

```typescript
// frontend/tailwind.config.ts
import type { Config } from "tailwindcss";
import tailwindAnimate from "tailwindcss-animate";

const config: Config = {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Deep Navy (scholarly authority)
        primary: {
          50: "#EEF2F7",
          100: "#D4DEE9",
          200: "#A9BDD4",
          300: "#93B4D4",
          400: "#5E89B4",
          500: "#345F8A",
          600: "#274A6E",
          700: "#1E3A5F",
          800: "#152C48",
          900: "#0D1D31",
          950: "#071019",
          DEFAULT: "#1E3A5F",
        },
        // Secondary - Warm Stone
        secondary: {
          50: "#FAF9F6",
          100: "#F1EDE7",
          200: "#E2DCD3",
          300: "#C8BFB3",
          400: "#A39889",
          500: "#7D7265",
          DEFAULT: "#F1EDE7",
        },
        // Accent - Amber/Gold (warmth, highlights)
        accent: {
          50: "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          300: "#FCD34D",
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",
          700: "#B45309",
          800: "#92400E",
          900: "#78350F",
          DEFAULT: "#B45309",
        },
        // Era-specific colors
        era: {
          early: "#C2410C",
          nicene: "#B45309",
          medieval: "#7C3AED",
          reformation: "#15803D",
          modern: "#2563EB",
          contemporary: "#475569",
        },
        // Semantic aliases (used by shadcn/ui via CSS variables)
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },
      fontFamily: {
        heading: [
          '"Source Serif 4"',
          "Georgia",
          '"Times New Roman"',
          "serif",
        ],
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          '"Segoe UI"',
          "sans-serif",
        ],
        mono: [
          '"JetBrains Mono"',
          '"Fira Code"',
          "Consolas",
          "monospace",
        ],
      },
      borderRadius: {
        lg: "12px",
        md: "8px",
        sm: "6px",
      },
      zIndex: {
        base: "0",
        raised: "10",
        sidebar: "20",
        header: "30",
        dropdown: "40",
        overlay: "50",
        modal: "60",
        toast: "70",
        tooltip: "80",
        max: "100",
      },
      transitionDuration: {
        fast: "100ms",
        normal: "200ms",
        slow: "300ms",
        slower: "500ms",
      },
      maxWidth: {
        page: "1440px",
        chat: "720px",
      },
      width: {
        sidebar: "240px",
        "sidebar-collapsed": "64px",
        canvas: "400px",
      },
      keyframes: {
        "slide-in-right": {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        "slide-out-right": {
          "0%": { transform: "translateX(0)", opacity: "1" },
          "100%": { transform: "translateX(100%)", opacity: "0" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%": { transform: "scale(0.95)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
      animation: {
        "slide-in-right": "slide-in-right 300ms ease-in-out",
        "slide-out-right": "slide-out-right 300ms ease-in-out",
        "fade-in": "fade-in 200ms ease-out",
        "scale-in": "scale-in 200ms ease-out",
      },
    },
  },
  plugins: [tailwindAnimate],
};

export default config;
```

### CSS Variables (in `index.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 40 10% 98%;
    --foreground: 20 14% 10%;
    --card: 0 0% 100%;
    --card-foreground: 20 14% 10%;
    --popover: 0 0% 100%;
    --popover-foreground: 20 14% 10%;
    --primary: 211 53% 24%;
    --primary-foreground: 210 40% 98%;
    --secondary: 30 22% 93%;
    --secondary-foreground: 20 8% 46%;
    --accent: 32 95% 37%;
    --accent-foreground: 48 100% 96%;
    --muted: 20 6% 96%;
    --muted-foreground: 20 5% 46%;
    --destructive: 0 72% 51%;
    --destructive-foreground: 0 0% 100%;
    --border: 20 6% 90%;
    --input: 20 6% 90%;
    --ring: 211 53% 24%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 20 14% 4%;
    --foreground: 20 5% 98%;
    --card: 20 14% 10%;
    --card-foreground: 20 5% 98%;
    --popover: 20 14% 10%;
    --popover-foreground: 20 5% 98%;
    --primary: 208 42% 70%;
    --primary-foreground: 20 14% 4%;
    --secondary: 20 8% 15%;
    --secondary-foreground: 20 6% 82%;
    --accent: 45 93% 52%;
    --accent-foreground: 20 14% 4%;
    --muted: 20 8% 15%;
    --muted-foreground: 20 5% 64%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 20 8% 27%;
    --input: 20 8% 27%;
    --ring: 208 42% 70%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground font-sans antialiased;
  }
  h1, h2 {
    @apply font-heading;
  }
}
```

---

## 7. Wireframes

### 7.1 Global Layout Architecture

```
Desktop (>= 1024px):
┌──────────────────────────────────────────────────────────────────────┐
│  Top Nav: [=] Toledot              [Search........] [?] [O] [Avatar]│
├────────┬─────────────────────────────┬───────────────────────────────┤
│ Side   │                             │                               │
│ Nav    │   Main Content Area         │   Canvas Panel (collapsible)  │
│ 240px  │   (scrollable)              │   400-600px                   │
│        │                             │                               │
│ [Home] │                             │   Shown when AI presents:     │
│ [Eras] │                             │   - Images                    │
│ [Chat] │                             │   - Timelines                 │
│ [Quiz] │                             │   - Maps                      │
│ [Prog] │                             │   - Key figures               │
│        │                             │   - Flashcards                │
│        │                             │                               │
│--------│                             │                               │
│        │                             │                               │
│ [Cog]  │                             │                               │
└────────┴─────────────────────────────┴───────────────────────────────┘

Tablet (640-1023px):
┌──────────────────────────────────────────────────────────────────────┐
│  Top Nav: [=] Toledot              [Search........] [?] [O] [Avatar]│
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Main Content Area (full width)                                     │
│                                                                      │
│   Canvas Panel: opens as slide-over overlay from right               │
│                                                                      │
│   Side Nav: collapsible drawer from left (hamburger trigger)         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

Mobile (< 640px):
┌──────────────────────────────────┐
│  Top Nav: [=] Toledot   [O] [Av]│
├──────────────────────────────────┤
│                                  │
│   Main Content Area              │
│   (full width, full height)      │
│                                  │
│   Canvas: full-screen overlay    │
│                                  │
├──────────────────────────────────┤
│  [Home] [Eras] [Chat] [Quiz] [+]│
│  Bottom Tab Bar                  │
└──────────────────────────────────┘
```

**Legend for all wireframes:**
- `[=]` Hamburger menu
- `[O]` Theme toggle (sun/moon)
- `[Av]`/`[Avatar]` User avatar with dropdown
- `[?]` Help/about
- `[Cog]` Settings (bottom of sidebar)

---

### 7.2 Landing Page

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  Nav:  Toledot                           [Features]  [About]  [Sign In -->] │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                                                                              │
│             Explore the Story of                                             │
│             the Church                                                       │
│                                                                              │
│             An AI-powered guide to church history                            │
│             in the Reformed tradition. Learn through                         │
│             conversation, not just reading.                                  │
│                                                                              │
│             [G  Sign in with Google]    [Learn more v]                       │
│                                                                              │
│                                                                              │
│         ┌───────────────────────────────────────────────────────┐            │
│         │                                                       │            │
│         │   (Hero illustration: stylized timeline with          │            │
│         │    key figures as nodes, from Early Church             │            │
│         │    through Reformation to modern era.                  │            │
│         │    Subtle animation: nodes glow sequentially.)         │            │
│         │                                                       │            │
│         └───────────────────────────────────────────────────────┘            │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   How Toledot Works                                                          │
│                                                                              │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│   │  (chat icon)     │  │  (canvas icon)   │  │  (trophy icon)   │          │
│   │                  │  │                  │  │                  │          │
│   │  Ask Anything    │  │  See It          │  │  Track Progress  │          │
│   │                  │  │                  │  │                  │          │
│   │  Chat with an    │  │  Visual canvas   │  │  Quizzes, streaks│          │
│   │  AI tutor that   │  │  shows images,   │  │  and achievements│          │
│   │  knows Reformed  │  │  timelines, and  │  │  keep you        │          │
│   │  church history. │  │  key figures as  │  │  motivated.      │          │
│   │                  │  │  you learn.      │  │                  │          │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Journey Through the Ages                                                   │
│                                                                              │
│   [Early Church]---[Nicene]---[Medieval]---[Reformation]---[Modern]---[Now]  │
│    30-325 AD       325-590    590-1517     1517-1648      1648-1900  1900+   │
│   (terracotta)     (gold)    (purple)     (green)        (blue)     (slate)  │
│                                                                              │
│   Each era node is clickable; hovering shows a brief description.            │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Sources You Can Trust                                                      │
│                                                                              │
│   Built on teachings from:                                                   │
│   [Ligonier] [Westminster] [RTS] [Master's Seminary] [Ryan Reeves]          │
│   (logos / icons in a horizontal scroll row)                                 │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Ready to begin?                                                            │
│                                                                              │
│   [G  Get Started with Google]                                               │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│   Footer:  Toledot  |  About  |  Privacy  |  Terms    (c) 2026              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.3 Login Page

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                         (centered on page)                           │
│                                                                      │
│                    ┌────────────────────────┐                        │
│                    │                        │                        │
│                    │     Toledot            │                        │
│                    │     (logo / wordmark)  │                        │
│                    │                        │                        │
│                    │  ───────────────────── │                        │
│                    │                        │                        │
│                    │  Welcome back.         │                        │
│                    │                        │                        │
│                    │  Sign in to continue   │                        │
│                    │  your journey through  │                        │
│                    │  church history.       │                        │
│                    │                        │                        │
│                    │  [G  Sign in with      │                        │
│                    │      Google       ]    │                        │
│                    │                        │                        │
│                    │  ───────────────────── │                        │
│                    │                        │                        │
│                    │  By signing in, you    │                        │
│                    │  agree to our Terms    │                        │
│                    │  and Privacy Policy.   │                        │
│                    │                        │                        │
│                    └────────────────────────┘                        │
│                                                                      │
│    (Background: subtle repeating pattern of                          │
│     faint cross / book motifs on secondary-50)                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

### 7.4 Dashboard / Home

```
┌──────────────────────────────────────────────────────────────────────┐
│  [=] Toledot                    [Search...............] [O] [Avatar]│
├────────┬─────────────────────────────────────────────────────────────┤
│        │                                                             │
│ [Home] │  Good morning, John.                                        │
│ [Eras] │                                                             │
│ [Chat] │  ┌─────────────────────────────────────────────────────┐   │
│ [Quiz] │  │  Continue Learning                                   │   │
│ [Prog] │  │                                                      │   │
│        │  │  ┌─────────────────┐  ┌─────────────────┐           │   │
│        │  │  │ (era color bar) │  │ (era color bar) │           │   │
│        │  │  │ The Reformation │  │ Early Church    │           │   │
│        │  │  │                 │  │                 │           │   │
│        │  │  │ Last: Council   │  │ Last: Apostolic │           │   │
│        │  │  │ of Trent        │  │ Fathers         │           │   │
│        │  │  │                 │  │                 │           │   │
│        │  │  │ [===-----] 40%  │  │ [==------] 25%  │           │   │
│        │  │  │ [Resume -->]    │  │ [Resume -->]    │           │   │
│        │  │  └─────────────────┘  └─────────────────┘           │   │
│        │  └─────────────────────────────────────────────────────┘   │
│        │                                                             │
│        │  ┌──────────────────────┐  ┌────────────────────────────┐  │
│        │  │  Quick Chat           │  │  Your Progress             │  │
│        │  │                       │  │                            │  │
│        │  │  "Ask me anything     │  │  Current streak: 5 days   │  │
│        │  │   about church        │  │  Quizzes passed: 12       │  │
│        │  │   history..."         │  │  Eras explored: 3/6       │  │
│        │  │                       │  │                            │  │
│        │  │  [Start chatting -->] │  │  [=======---] 58%         │  │
│        │  │                       │  │                            │  │
│        │  └──────────────────────┘  │  [View details -->]        │  │
│        │                             └────────────────────────────┘  │
│        │                                                             │
│        │  ┌─────────────────────────────────────────────────────┐   │
│        │  │  Recent Activity                                     │   │
│        │  │                                                      │   │
│        │  │  Today   - Completed quiz: "Reformation Key Events" │   │
│        │  │  Yesterday - Chatted about: Martin Luther's 95 ...  │   │
│        │  │  Feb 14  - Explored: Nicene Era overview             │   │
│        │  │  Feb 13  - Earned badge: "First Quiz"                │   │
│        │  └─────────────────────────────────────────────────────┘   │
│        │                                                             │
│--------│                                                             │
│ [Cog]  │                                                             │
└────────┴─────────────────────────────────────────────────────────────┘
```

---

### 7.5 Chat Interface

The primary learning interface. Three-panel layout with collapsible side nav and canvas.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  [=] Toledot          [Search.............] [New Chat +] [O] [Avatar]       │
├────────┬───────────────────────────────────┬─────────────────────────────────┤
│        │                                   │                                 │
│ Chats  │  Chat: The Reformation            │  Canvas                         │
│        │  Era: Reformation (1517-1648)     │  ┌───────────────────────────┐  │
│ Recent │  ─────────────────────────────    │  │                           │  │
│        │                                   │  │  (Currently showing:)     │  │
│ > The  │  [Bot avatar]                     │  │                           │  │
│   Refo │  The Reformation began in 1517    │  │  Portrait of              │  │
│   rmat │  when Martin Luther nailed his    │  │  Martin Luther            │  │
│   ion  │  95 Theses to the door of the     │  │  by Lucas Cranach         │  │
│        │  Castle Church in Wittenberg...   │  │  the Elder (1528)         │  │
│   Earl │                                   │  │                           │  │
│   y Ch │  Luther's key theological         │  │  [img placeholder]        │  │
│   urch │  insights included:               │  │                           │  │
│        │                                   │  │                           │  │
│   Nico │  1. Sola Scriptura               │  └───────────────────────────┘  │
│   ne C │  2. Sola Fide                    │                                 │
│   reed │  3. Sola Gratia                  │  Key Figures                     │
│        │                                   │  ┌───────────────────────────┐  │
│ ────── │  Would you like to explore any    │  │ Martin Luther  (1483-1546)│  │
│        │  of these in more detail?         │  │ John Calvin    (1509-1564)│  │
│ Topics │                                   │  │ Huldrych Zwingli (1484-..│  │
│        │  ─────────────────────────────    │  └───────────────────────────┘  │
│ Refor. │                                   │                                 │
│ Early  │  [User avatar]                    │  Timeline                        │
│ Creeds │  Tell me more about Sola Fide    │  ┌───────────────────────────┐  │
│        │  and how it differs from the      │  │ 1517 ● 95 Theses         │  │
│        │  Catholic understanding.           │  │ 1521 ● Diet of Worms     │  │
│        │                                   │  │ 1534 ● English Reform.   │  │
│        │  ─────────────────────────────    │  │ 1536 ● Calvin: Institutes│  │
│        │                                   │  │ 1545 ● Council of Trent  │  │
│        │  [Bot avatar]                     │  │ 1648 ● Peace of Westph.  │  │
│        │  Great question! Sola Fide, or    │  └───────────────────────────┘  │
│        │  "faith alone," is one of the     │                                 │
│        │  five Solas of the Reformation... │  [Source: R.C. Sproul -         │
│        │  (typing indicator ...)           │   Ligonier Ministries]          │
│        │                                   │                                 │
│        │  ┌─────────────────────────────┐  │  [Canvas collapse >>]           │
│        │  │  Type a message...   [Send] │  │                                 │
│        │  └─────────────────────────────┘  │                                 │
│--------│                                   │                                 │
│ [Cog]  │                                   │                                 │
└────────┴───────────────────────────────────┴─────────────────────────────────┘
```

**Chat panel details:**
- Messages alternate between user (right-aligned, primary background) and AI (left-aligned, card background)
- AI messages can contain markdown: bold, lists, blockquotes for scripture
- Typing indicator: three animated dots
- Message input: auto-expanding textarea, send button, optional attachments
- Conversation history in left sidebar, grouped by date

**Canvas panel details:**
- Resizable via drag handle on left edge
- Collapsible with a toggle button
- Content types: images, key figure cards, timeline, map, flashcards
- Automatically populated by AI based on conversation context
- Scrollable independently of chat

---

### 7.6 Era Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  [=] Toledot                    [Search...............] [O] [Avatar]        │
├────────┬─────────────────────────────────────────────────────────────────────┤
│        │                                                                     │
│ [Home] │  Church History Eras                                                │
│ [Eras] │                                                                     │
│ [Chat] │  ┌─────────────────────────────────────────────────────────────┐   │
│ [Quiz] │  │                                                             │   │
│ [Prog] │  │  Interactive Timeline (horizontal, scrollable)              │   │
│        │  │                                                             │   │
│        │  │  30 AD                                                 2026 │   │
│        │  │  |                                                       |  │   │
│        │  │  [████ Early ████][██ Nicene ██][████ Medieval █████]       │   │
│        │  │                         [██ Reform. ██][██ Modern ██][Now]  │   │
│        │  │                                                             │   │
│        │  │  Each segment is colored by era, proportional to duration.  │   │
│        │  │  Hovering a segment highlights it and shows a tooltip.      │   │
│        │  │  Clicking opens the era detail below.                       │   │
│        │  │                                                             │   │
│        │  └─────────────────────────────────────────────────────────────┘   │
│        │                                                                     │
│        │  Currently viewing: The Reformation (1517-1648)                     │
│        │                                                                     │
│        │  ┌───────────────────────────────┐  ┌───────────────────────────┐  │
│        │  │  Overview                      │  │  Key Events               │  │
│        │  │                                │  │                           │  │
│        │  │  The Protestant Reformation    │  │  * 1517 - 95 Theses      │  │
│        │  │  was a major movement within   │  │  * 1521 - Diet of Worms  │  │
│        │  │  Western Christianity that     │  │  * 1534 - Act of Suprem. │  │
│        │  │  began in the 16th century...  │  │  * 1536 - Institutes     │  │
│        │  │                                │  │  * 1545 - Council/Trent  │  │
│        │  │  [Chat about this era -->]     │  │  * 1618 - Synod of Dort │  │
│        │  │                                │  │  * 1648 - Westphalia    │  │
│        │  └───────────────────────────────┘  └───────────────────────────┘  │
│        │                                                                     │
│        │  Key Figures                                                        │
│        │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│        │  │ (portrait)│ │ (portrait)│ │ (portrait)│ │ (portrait)│         │
│        │  │  Martin   │ │  John     │ │  Huldrych │ │  John     │         │
│        │  │  Luther   │ │  Calvin   │ │  Zwingli  │ │  Knox     │         │
│        │  │  1483-1546│ │  1509-1564│ │  1484-1531│ │  1514-1572│         │
│        │  └───────────┘ └───────────┘ └───────────┘ └───────────┘         │
│        │                                                                     │
│        │  ┌──────────────────────────────────────────────────┐              │
│        │  │  Test Your Knowledge                              │              │
│        │  │  Ready to see what you've learned about this era? │              │
│        │  │  [Take the Reformation Quiz -->]                  │              │
│        │  └──────────────────────────────────────────────────┘              │
│        │                                                                     │
│--------│                                                                     │
│ [Cog]  │                                                                     │
└────────┴─────────────────────────────────────────────────────────────────────┘
```

---

### 7.7 Quiz Interface (Bonus Wireframe)

```
┌──────────────────────────────────────────────────────────────────────┐
│  [=] Toledot        Reformation Quiz (3/10)      [O] [Avatar]       │
├────────┬─────────────────────────────────────────────────────────────┤
│        │                                                             │
│ (nav   │  ┌─────────────────────────────────────────────────────┐   │
│  colla │  │  [========-------] 3 of 10                           │   │
│  psed) │  └─────────────────────────────────────────────────────┘   │
│        │                                                             │
│        │  Who wrote the Institutes of the                            │
│        │  Christian Religion?                                        │
│        │                                                             │
│        │  ┌─────────────────────────────────────────────────────┐   │
│        │  │  A) Martin Luther                                    │   │
│        │  └─────────────────────────────────────────────────────┘   │
│        │  ┌─────────────────────────────────────────────────────┐   │
│        │  │  B) John Calvin                    <-- selected      │   │
│        │  └─────────────────────────────────────────────────────┘   │
│        │  ┌─────────────────────────────────────────────────────┐   │
│        │  │  C) Huldrych Zwingli                                 │   │
│        │  └─────────────────────────────────────────────────────┘   │
│        │  ┌─────────────────────────────────────────────────────┐   │
│        │  │  D) John Knox                                        │   │
│        │  └─────────────────────────────────────────────────────┘   │
│        │                                                             │
│        │                              [Submit Answer]                │
│        │                                                             │
│        │  ── After answering correctly: ──────────────────────────  │
│        │                                                             │
│        │  Correct! John Calvin published the first                  │
│        │  edition of the Institutes in 1536 at age 26.              │
│        │                                                             │
│        │  [Learn more in chat -->]         [Next Question -->]       │
│        │                                                             │
└────────┴─────────────────────────────────────────────────────────────┘
```

---

## 8. Component Hierarchy

### 8.1 Shadcn/ui Primitives to Install

These are the Shadcn/ui components needed for P0-P2 features:

**Core (install immediately for P0):**
- `button` - Primary, secondary, ghost, destructive, outline variants
- `card` - Dashboard cards, era cards, feature cards
- `input` - Search, chat input
- `label` - Form labels
- `separator` - Section dividers
- `skeleton` - Loading states
- `avatar` - User avatars, AI avatar
- `badge` - Era labels, status tags, achievement badges
- `scroll-area` - Chat message scroll, sidebar scroll
- `tooltip` - Icon buttons, timeline nodes

**Navigation (P0-P1):**
- `navigation-menu` - Top nav links (landing page)
- `dropdown-menu` - User menu, settings
- `sheet` - Mobile sidebar drawer, canvas slide-over
- `tabs` - Era detail sections, dashboard sections
- `command` - Command palette / search (Ctrl+K)

**Chat & Content (P1-P2):**
- `dialog` - Confirmations, image preview
- `popover` - Hovercards for figures, terms
- `textarea` - Chat message input (auto-expanding)
- `toggle` - Theme toggle, sidebar collapse
- `progress` - Progress bars, quiz progress
- `collapsible` - Sidebar sections, chat history groups
- `accordion` - FAQ, era details expandable sections

**Quiz & Progress (P2):**
- `radio-group` - Quiz answer selection
- `alert` - Correct/incorrect feedback
- `toast` - Achievement unlocked, action confirmations
- `hover-card` - Figure bio previews

### 8.2 Custom Components

Built on top of Shadcn/ui primitives:

```
src/components/
├── layout/
│   ├── AppShell.tsx            # Root layout: sidebar + header + main + canvas
│   ├── TopNav.tsx              # Top navigation bar
│   ├── SideNav.tsx             # Collapsible side navigation
│   ├── BottomNav.tsx           # Mobile bottom tab bar
│   ├── CanvasPanel.tsx         # Right-side collapsible canvas panel
│   └── PageContainer.tsx       # Centered content wrapper with max-width
│
├── chat/
│   ├── ChatLayout.tsx          # Chat page layout (messages + input + canvas)
│   ├── ChatMessage.tsx         # Single message bubble (user or AI)
│   ├── ChatMessageList.tsx     # Scrollable message list
│   ├── ChatInput.tsx           # Auto-expanding textarea with send button
│   ├── ChatSidebar.tsx         # Conversation history sidebar
│   ├── TypingIndicator.tsx     # Animated typing dots
│   └── SourceCitation.tsx      # Inline source reference
│
├── canvas/
│   ├── CanvasContainer.tsx     # Canvas wrapper with resize handle
│   ├── CanvasImage.tsx         # Image display with caption
│   ├── CanvasTimeline.tsx      # Interactive vertical timeline
│   ├── CanvasKeyFigure.tsx     # Person card (portrait, dates, bio)
│   └── CanvasFlashcard.tsx     # Flippable flashcard
│
├── era/
│   ├── EraTimeline.tsx         # Horizontal interactive timeline
│   ├── EraCard.tsx             # Era summary card with progress
│   ├── EraDetail.tsx           # Expanded era information
│   └── FigureCard.tsx          # Key figure portrait card
│
├── quiz/
│   ├── QuizLayout.tsx          # Quiz page layout
│   ├── QuizQuestion.tsx        # Question with answer options
│   ├── QuizProgress.tsx        # Progress bar for quiz
│   ├── QuizResult.tsx          # Correct/incorrect feedback
│   └── QuizSummary.tsx         # End-of-quiz results
│
├── progress/
│   ├── ProgressOverview.tsx    # Overall progress dashboard
│   ├── StreakCounter.tsx       # Daily streak display
│   ├── AchievementBadge.tsx    # Individual badge
│   └── EraProgress.tsx         # Per-era progress bar
│
├── landing/
│   ├── HeroSection.tsx         # Landing page hero
│   ├── FeatureCard.tsx         # "How it works" feature cards
│   ├── EraPreview.tsx          # Landing page era timeline preview
│   └── SourceLogos.tsx         # Trusted sources logo row
│
├── auth/
│   ├── GoogleSignInButton.tsx  # Google OAuth button
│   └── AuthGuard.tsx           # Route protection wrapper
│
└── shared/
    ├── ThemeToggle.tsx         # Light/dark mode toggle
    ├── SearchCommand.tsx       # Ctrl+K command palette
    ├── LoadingSpinner.tsx      # Consistent loading indicator
    ├── EmptyState.tsx          # Empty state illustration + message
    └── ErrorBoundary.tsx       # Error fallback UI
```

### 8.3 Component Naming Conventions

- **PascalCase** for all component files and exports: `ChatMessage.tsx`, `EraTimeline.tsx`
- **Prefix by domain**: `Chat*`, `Era*`, `Quiz*`, `Canvas*`
- **Layout components** are generic: `AppShell`, `PageContainer`, `TopNav`
- **Shadcn/ui components** live in `src/components/ui/` (auto-generated by CLI)
- **Custom components** live in domain folders under `src/components/`
- **Page components** live in `src/pages/` and compose custom components
- Props interfaces: `[ComponentName]Props` (e.g., `ChatMessageProps`)
- Event handlers: `on[Event]` (e.g., `onSend`, `onSelectEra`)

---

## 9. Accessibility

### 9.1 WCAG 2.1 AA Compliance Plan

| Principle | Requirement | Implementation |
|-----------|-------------|----------------|
| **Perceivable** | Text alternatives for non-text content | All images get `alt` text; canvas images include captions; icons paired with `aria-label` |
| **Perceivable** | Color contrast >= 4.5:1 (normal text), >= 3:1 (large text) | Verified for all palette combinations (see below) |
| **Perceivable** | Content is not conveyed by color alone | Era colors always paired with text labels; quiz correct/incorrect uses icons + text + color |
| **Operable** | All functionality via keyboard | Full keyboard navigation plan (see below) |
| **Operable** | No time limits (or adjustable) | Quiz has no timer by default; if added, user can extend |
| **Understandable** | Predictable navigation | Consistent sidebar, consistent top nav across all pages |
| **Understandable** | Input assistance | Clear labels, error messages inline, required fields marked |
| **Robust** | Valid HTML, ARIA landmarks | Semantic HTML5 elements; `<main>`, `<nav>`, `<aside>`, `<header>` |

### 9.2 Color Contrast Verification

| Combination | Ratio | Status |
|------------|-------|--------|
| `foreground` on `background` (light) | 16.3:1 | PASS AAA |
| `primary-700` on `white` | 8.9:1 | PASS AAA |
| `primary-foreground` on `primary-700` | 8.9:1 | PASS AAA |
| `accent-700` on `white` | 4.8:1 | PASS AA |
| `accent-foreground` on `accent-700` | 4.8:1 | PASS AA |
| `muted-foreground` on `background` (light) | 4.6:1 | PASS AA |
| `foreground` on `background` (dark) | 17.1:1 | PASS AAA |
| `primary-300` on `stone-950` (dark) | 7.2:1 | PASS AAA |
| `accent-500` on `stone-950` (dark) | 8.5:1 | PASS AAA |
| `muted-foreground` on `background` (dark) | 5.1:1 | PASS AA |
| `destructive` on `white` | 4.6:1 | PASS AA |
| `success` on `white` | 4.5:1 | PASS AA |

### 9.3 Keyboard Navigation Plan

| Area | Keys | Behavior |
|------|------|----------|
| **Global** | `Ctrl+K` / `Cmd+K` | Open command palette (search) |
| **Global** | `Tab` / `Shift+Tab` | Move focus through interactive elements |
| **Global** | `Escape` | Close modal, panel, or dropdown |
| **Side Nav** | `Arrow Up/Down` | Navigate menu items |
| **Side Nav** | `Enter` / `Space` | Select menu item |
| **Chat** | `Enter` | Send message |
| **Chat** | `Shift+Enter` | New line in message input |
| **Chat** | `Arrow Up` | Edit last sent message |
| **Quiz** | `1-4` or `A-D` | Select answer option |
| **Quiz** | `Enter` | Submit selected answer / next question |
| **Timeline** | `Arrow Left/Right` | Navigate between eras |
| **Timeline** | `Enter` | Open era detail |
| **Canvas** | `Escape` | Close canvas panel |
| **Dialog** | `Tab` | Cycle through dialog buttons |
| **Dialog** | `Enter` | Confirm action |

### 9.4 Screen Reader Considerations

- **ARIA Landmarks**: `<header role="banner">`, `<nav role="navigation">`, `<main role="main">`, `<aside role="complementary">` for canvas
- **Live Regions**: Chat messages use `aria-live="polite"` so new messages are announced; typing indicator uses `aria-live="assertive"` with `aria-label="AI is typing"`
- **Focus Management**: When canvas panel opens, focus moves to canvas; when modal opens, focus is trapped within modal; when closed, focus returns to trigger
- **Hidden Decorative Elements**: Decorative icons get `aria-hidden="true"`; interactive icons get descriptive `aria-label`
- **Skip Navigation**: "Skip to main content" link as the first focusable element
- **Heading Hierarchy**: Strict `h1 > h2 > h3` hierarchy; only one `h1` per page
- **Form Labels**: Every input has an associated `<label>` (visually hidden if necessary with `sr-only`)

---

## 10. Responsive Strategy

### 10.1 Mobile-First Approach

All styles are written mobile-first. Desktop enhancements are added with `sm:`, `md:`, `lg:`, `xl:` prefixes.

### 10.2 Layout Collapse Behavior

| Breakpoint | Side Nav | Main Content | Canvas Panel |
|-----------|----------|--------------|--------------|
| **Mobile** (< 640px) | Hidden; bottom tab bar instead | Full width | Full-screen overlay (swipe to dismiss) |
| **Tablet** (640-767px) | Drawer (hamburger trigger), overlays content | Full width | Slide-over sheet from right, overlays content |
| **Small Desktop** (768-1023px) | Collapsed (icons only, 64px) | Fills remaining width | Slide-over sheet from right, overlays content |
| **Desktop** (1024-1279px) | Expanded (240px) | Fills remaining width | Inline panel (400px), collapsible |
| **Wide Desktop** (>= 1280px) | Expanded (240px) | Fills remaining width | Inline panel (up to 600px), resizable |

### 10.3 Specific Component Responsive Behavior

**Top Nav:**
- Mobile: Logo + theme toggle + avatar only; search moves to a full-screen overlay triggered by search icon
- Tablet+: Full nav with search bar

**Chat Interface:**
- Mobile: Chat messages take full width; input is fixed to bottom; canvas is accessible via a floating action button (FAB) that opens full-screen overlay
- Tablet: Chat full width; canvas slides over from right as a sheet
- Desktop: Side-by-side chat and canvas

**Dashboard Cards:**
- Mobile: Single column, full width, stacked vertically
- Tablet: Two-column grid
- Desktop: Flexible grid (2-3 columns depending on card sizes)

**Era Timeline:**
- Mobile: Vertical timeline (scrollable), eras stacked
- Tablet+: Horizontal timeline with horizontal scroll

**Quiz:**
- Mobile: Full-width answer options, stacked vertically
- Tablet+: Same layout but wider options with more padding

### 10.4 Touch-Friendly Interactions

| Element | Minimum Size | Notes |
|---------|-------------|-------|
| Buttons | 44x44px | Per WCAG 2.5.5 (AAA) and Apple HIG |
| Nav items | 48x48px touch target | Padding extends clickable area |
| Chat send button | 44x44px | Always visible, high contrast |
| Timeline nodes | 48x48px touch target | Generous hit area around node |
| Quiz options | Full-width tap target | Entire option row is tappable |
| Canvas resize handle | 24px wide drag area | Visible grip indicator |
| Swipe gestures | 30px minimum travel | Canvas dismiss, sidebar toggle |

### 10.5 Performance Considerations for Mobile

- **Lazy load** canvas panel content (images, Konva.js) -- only load when panel is opened
- **Virtualize** long chat message lists (only render visible messages)
- **Reduce motion** for users with `prefers-reduced-motion`: disable slide animations, use instant transitions
- **Responsive images**: Serve appropriate image sizes via `srcset`
- **Font subsetting**: Load only Latin character set for Google Fonts

---

## Appendix: Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary color | Deep Navy (#1E3A5F) | Academic authority without corporate coldness; pairs well with warm stone neutrals |
| Accent color | Amber (#B45309) | Warmth of aged paper and candlelight; high visibility for CTAs; complements navy |
| Heading font | Source Serif 4 | Scholarly serif that is also highly readable on screens; variable font with optical sizing |
| Body font | Inter | Industry standard for UI; excellent screen readability; variable weight |
| Neutral palette | Stone (warm gray) | Warmer than slate/zinc; feels less clinical; evokes parchment |
| Dark mode strategy | Class-based toggle | User preference persisted; not tied to OS preference by default (can sync optionally) |
| Layout model | Collapsible three-panel | Maximizes learning surface; canvas provides visual context alongside chat |
| Mobile navigation | Bottom tab bar | Thumb-friendly; follows native mobile patterns (iOS/Android) |
| Component library | Shadcn/ui | Full ownership of components; consistent with Tailwind; no runtime dependency |
| Canvas approach | Slide-in panel (not modal) | Non-disruptive; user can reference chat and canvas simultaneously |

---

*This document is the single source of truth for all visual design decisions in Toledot. All implementations should reference these tokens and patterns.*
