# Licensing Policy

## Allowed Licenses (Commercially Permissive)

The following open-source licenses are approved for use in this project:

| License | SPDX Identifier | Notes |
|---|---|---|
| MIT License | MIT | Preferred |
| Apache License 2.0 | Apache-2.0 | Preferred |
| BSD 2-Clause | BSD-2-Clause | Allowed |
| BSD 3-Clause | BSD-3-Clause | Allowed |
| ISC License | ISC | Allowed |
| PostgreSQL License | PostgreSQL | Allowed |
| The Unlicense | Unlicense | Allowed |
| CC0 1.0 | CC0-1.0 | Allowed (for data/content) |
| Python Software Foundation | PSF-2.0 | Allowed |
| Zlib License | Zlib | Allowed |

## Prohibited Licenses

| License | Reason |
|---|---|
| GPL v2/v3 | Copyleft - forces derivative works to be GPL |
| AGPL v3 | Network copyleft - even server use triggers obligations |
| LGPL | Copyleft (acceptable only for dynamically linked libraries, case-by-case) |
| SSPL | Server-side restrictions |
| CC-BY-NC | Non-commercial restriction |
| CC-BY-SA | Share-alike copyleft |

## Review Process

1. **Before adding any new dependency**, verify its license.
2. Run `pip-audit` (Python) and `npm audit` (Node) before each release.
3. Use `pip-licenses` to generate a license report for Python dependencies.
4. Use `license-checker` (npm) for JavaScript dependencies.
5. Document any exceptions in this file with justification.

## Exceptions

None currently.

## Content Licensing

- Scraped content is used under fair use for educational purposes.
- All source attributions are maintained in the database.
- Users are shown source citations with links to original content.
