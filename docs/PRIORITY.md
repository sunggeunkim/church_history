# Feature Priority & Roadmap

## Prioritization Rationale

Features are ordered based on technical dependencies. Each feature builds on the previous one. We implement one feature at a time with full branch-based workflow (branch → develop → PR → merge).

---

## Priority Order

### P0: Project Foundation & App Naming (Sprint 0)
**Features Covered:** #11 (App Naming), Project Setup
- **Why First:** Everything depends on having a named project with proper infrastructure.
- Research Hebrew/Greek names for the app
- Set up Django backend with DRF
- Set up React frontend (Vite + TypeScript)
- Set up PostgreSQL with pgvector extension
- Docker Compose for local development
- CI/CD skeleton
- **Branch:** `feature/project-foundation`

### P1: Google OAuth Authentication (Sprint 1)
**Features Covered:** #9 (Google OAuth)
- **Why Second:** User identity is required for progress tracking, sharing, and personalization.
- Django Allauth with Google OAuth provider
- JWT token-based auth for React SPA
- User profile model
- Protected routes on frontend
- **Branch:** `feature/google-oauth`

### P2: Content Scraping Pipeline (Sprint 2)
**Features Covered:** #5 (Scraping), #4 (Reformed Tradition)
- **Why Third:** AI agent needs data before it can teach. This is the data foundation.
- YouTube transcript scraping (Ryan Reeves, Ligonier, Westminster seminaries, etc.)
- Blog/article scraping (Ligonier Ministries, seminary sites)
- Text chunking and vector embedding (pgvector)
- Django management commands for scraping
- Content metadata tagging (era, topic, source, tradition)
- **Branch:** `feature/content-pipeline`

### P3: Church History Era Structure (Sprint 3)
**Features Covered:** #3 (Eras), #4 (Reformed Tradition)
- **Why Fourth:** Organizing content by era provides the curriculum backbone.
- Define eras: Early Church, Medieval, Reformation, Post-Reformation, Modern
- Era models with rich metadata
- Timeline API endpoints
- Frontend era navigation and timeline UI
- Map scraped content to eras
- **Branch:** `feature/church-history-eras`

### P4: AI Chat Agent (Sprint 4)
**Features Covered:** #1 (AI Chat), #4 (Reformed Tradition)
- **Why Fifth:** Core feature, but needs content (P2) and structure (P3) first.
- RAG pipeline with pgvector similarity search
- Chat API with streaming responses
- Chat UI with message history
- Context-aware responses grounded in reformed tradition
- Source citation in responses
- **Branch:** `feature/ai-chat`

### P5: Interactive Canvas (Sprint 5)
**Features Covered:** #2 (Canvas with pictures/tools)
- **Why Sixth:** Enhances the chat experience with visual learning.
- Canvas panel alongside chat
- Image display (portraits, maps, artifacts)
- Timeline visualization within canvas
- Interactive teaching tools (flashcards, concept maps)
- **Branch:** `feature/interactive-canvas`

### P6: Fun Tests & Quizzes (Sprint 6)
**Features Covered:** #7 (Fun Tests), #8 (Research Fun Learning)
- **Why Seventh:** Engagement feature that builds on content and AI.
- Research gamification best practices
- Multiple quiz formats (multiple choice, timeline ordering, matching, fill-in)
- AI-generated contextual quizzes
- Instant feedback with explanations
- **Branch:** `feature/fun-tests`

### P7: Progress Tracking & Rewards (Sprint 7)
**Features Covered:** #6 (Progress & Rewards)
- **Why Eighth:** Requires user auth (P1), content structure (P3), and quizzes (P6).
- Study progress dashboard
- Era completion tracking
- Achievement/badge system
- Streak tracking
- Visual progress indicators
- **Branch:** `feature/progress-rewards`

### P8: Social Sharing (Sprint 8)
**Features Covered:** #10 (Share Learning)
- **Why Last:** Social features build on top of all other features.
- Share quiz results
- Share study progress
- Shareable learning summaries
- Social media integration
- **Branch:** `feature/social-sharing`

---

## Cross-Cutting Concerns (Ongoing)
- **Feature #8:** Research what makes learning fun - applied to every feature
- **Feature #4:** Reformed tradition focus - embedded in all content features
- **Documentation:** Updated with every PR
- **Testing:** Every feature includes unit + integration tests
