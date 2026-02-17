# P0 Tech Stack - Preliminary Verification

> **Note:** This is a preliminary verification by the team lead to unblock development while the Researcher completes their comprehensive report. The Researcher's full findings in `p0-tech-research.md` will supersede this.

## License Verification (from ARCHITECTURE.md)

All proposed dependencies verified as commercially permissive:

### Backend (Python)
| Package | License | Verified |
|---|---|---|
| Django 5.x | BSD-3-Clause | Yes |
| djangorestframework | BSD-3-Clause | Yes |
| django-allauth | MIT | Yes |
| djangorestframework-simplejwt | MIT | Yes |
| django-cors-headers | MIT | Yes |
| python-decouple | MIT | Yes |
| celery | BSD-3-Clause | Yes |
| redis (python) | MIT | Yes |
| psycopg[binary] | LGPL-3.0 | **FLAG: LGPL** - use psycopg2-binary (BSD) or psycopg[c] (LGPL but dynamically linked, acceptable) |
| beautifulsoup4 | MIT | Yes |
| requests | Apache-2.0 | Yes |
| yt-dlp | Unlicense | Yes |
| sentence-transformers | Apache-2.0 | Yes |
| litellm | MIT | Yes |
| pytest | MIT | Yes |
| pytest-django | BSD-3-Clause | Yes |
| factory-boy | MIT | Yes |
| ruff | MIT | Yes |
| gunicorn | MIT | Yes |

**Action Item:** Use `psycopg2-binary` (BSD license) for PostgreSQL driver instead of `psycopg` (LGPL).

### Frontend (Node.js)
| Package | License | Verified |
|---|---|---|
| react, react-dom | MIT | Yes |
| vite | MIT | Yes |
| typescript | Apache-2.0 | Yes |
| react-router-dom | MIT | Yes |
| zustand | MIT | Yes |
| axios | MIT | Yes |
| @radix-ui/* (Shadcn) | MIT | Yes |
| tailwindcss | MIT | Yes |
| eslint | MIT | Yes |
| prettier | MIT | Yes |
| vitest | MIT | Yes |
| @testing-library/react | MIT | Yes |

All frontend dependencies are clean - MIT or Apache-2.0.

## Key Decisions for P0

1. **PostgreSQL driver:** Use `psycopg2-binary` (BSD) to avoid LGPL concerns
2. **pgvector:** Use `pgvector/pgvector:pg16` Docker image (PostgreSQL License)
3. **Django settings:** Split settings pattern (base/dev/prod) with `python-decouple`
4. **React setup:** Vite + TypeScript strict mode
5. **State management:** Zustand (lightweight, MIT)
6. **UI framework:** Shadcn/ui with Radix primitives (all MIT)

## Status
- Developers are **unblocked** to begin scaffolding
- Full research report pending from Researcher
