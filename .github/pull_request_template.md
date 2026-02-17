## Summary

<!-- Brief description of what this PR does and why -->

**Feature:** <!-- e.g., P0: Project Foundation & App Naming -->
**Branch:** <!-- e.g., feature/project-foundation -->

## Changes

<!-- Bulleted list of the key changes in this PR -->

-
-
-

## Motivation

<!-- Why are these changes needed? Link to feature requirements or issues -->

## How to Test

<!-- Step-by-step instructions for reviewers to verify this PR -->

1. `git checkout <branch>`
2. `cp .env.example .env` (and fill in any required values)
3. `docker compose up --build`
4. Navigate to `http://localhost` in your browser
5. Verify:
   - [ ] Frontend loads
   - [ ] API health-check responds at `/api/health/`
   - [ ] ...

## Screenshots

<!-- If applicable, add screenshots or terminal output showing the feature working -->

## Checklist

### Code Quality
- [ ] Code follows project conventions
- [ ] Backend linting passes (`ruff check backend/`)
- [ ] Frontend linting passes (`npm run lint`)
- [ ] Frontend formatting passes (`npx prettier --check src/`)
- [ ] No `console.log` or debug statements left in code
- [ ] No commented-out code left without explanation

### Testing
- [ ] Backend tests pass (`pytest`)
- [ ] Frontend tests pass (`npm run test`)
- [ ] New functionality has corresponding tests
- [ ] Manual testing performed (describe in "How to Test" above)

### Security
- [ ] No secrets, API keys, or credentials in committed code
- [ ] `.env.example` updated if new environment variables were added
- [ ] No SQL injection, XSS, or other OWASP vulnerabilities introduced
- [ ] `pip-audit` shows no critical vulnerabilities
- [ ] `npm audit` shows no critical vulnerabilities

### License Compliance
- [ ] All new Python dependencies have permissive licenses (MIT/Apache-2.0/BSD)
- [ ] All new npm dependencies have permissive licenses (MIT/Apache-2.0/BSD)
- [ ] Verified via `pip-licenses` and `license-checker`

### Docker
- [ ] `docker compose build` succeeds
- [ ] `docker compose up` brings up all services
- [ ] All health checks pass

### Documentation
- [ ] README updated if setup instructions changed
- [ ] Architecture docs updated if structure changed
- [ ] New environment variables documented in `.env.example`

## Related Issues

<!-- Link any related issues: Closes #123, Relates to #456 -->

## Reviewer Notes

<!-- Anything specific reviewers should pay attention to -->
