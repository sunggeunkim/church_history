# P1 Research: Google OAuth + Django + React SPA

## Table of Contents

1. [Recommended OAuth Flow for SPA](#1-recommended-oauth-flow-for-spa)
2. [dj-rest-auth Google Login Endpoint](#2-dj-rest-auth-google-login-endpoint)
3. [JWT Token Storage Best Practices](#3-jwt-token-storage-best-practices)
4. [React Google OAuth Integration](#4-react-google-oauth-integration)
5. [CORS and Cookie Configuration](#5-cors-and-cookie-configuration)
6. [Token Refresh Strategy](#6-token-refresh-strategy)
7. [Code Examples](#7-code-examples)
8. [Recommended Architecture for Toledot](#8-recommended-architecture-for-toledot)

---

## 1. Recommended OAuth Flow for SPA

### Authorization Code Flow (Recommended)

For a React SPA with a Django backend, the **Authorization Code Flow** is the correct choice:

1. React opens a Google popup (via `@react-oauth/google`) or redirects to Google
2. User consents; Google returns an **authorization code** to the frontend
3. React POSTs the `code` to Django (`POST /api/auth/google/`)
4. Django (dj-rest-auth) exchanges the code with Google for access/id tokens server-side
5. Django creates/logs in the user and returns JWT tokens (via httpOnly cookies)

**Why not Implicit Flow?** The implicit flow is deprecated by Google and returns tokens
directly to the browser, which is less secure. Authorization Code flow keeps the
client_secret on the server.

**Why not redirect-based flow through Django?** While possible (the current LoginPage
redirects to `/api/auth/google/login/`), it forces a full-page redirect and is harder to
handle in an SPA. The popup flow via `@react-oauth/google` provides a better UX and keeps
the SPA shell intact.

### Flow Diagram

```
React SPA                    Google                     Django Backend
    |                          |                              |
    |-- useGoogleLogin() ----->|                              |
    |   (popup opens)          |                              |
    |                          |                              |
    |<-- authorization code ---|                              |
    |   (popup closes)         |                              |
    |                          |                              |
    |-- POST /api/auth/google/ --------------------------->   |
    |   { "code": "4/0Axx..." }                               |
    |                          |                              |
    |                          |<-- exchange code for tokens --|
    |                          |-- return access+id tokens -->|
    |                          |                              |
    |                          |              create/login user|
    |                          |              set JWT cookies  |
    |                          |                              |
    |<---------------- 200 OK + Set-Cookie headers -----------|
    |   (access_token cookie, refresh_token cookie)           |
    |                          |                              |
    |-- GET /api/accounts/me/ (cookies sent automatically) -->|
    |<-- user profile data -----------------------------------|
```

---

## 2. dj-rest-auth Google Login Endpoint

### SocialLoginView

dj-rest-auth provides `SocialLoginView` which accepts a POST with:

| Field          | Required   | Description                                      |
|----------------|------------|--------------------------------------------------|
| `access_token` | Optional*  | OAuth2 access token (Implicit Grant)              |
| `code`         | Optional*  | Authorization code (Authorization Code Grant)     |
| `id_token`     | Optional   | OpenID Connect ID token (cannot be used alone)    |

*At least one of `access_token` or `code` is required.

### Backend View Configuration

```python
# apps/accounts/views.py
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "postmessage"   # CRITICAL: must be "postmessage" for popup flow
    client_class = OAuth2Client
```

**Key detail: `callback_url = "postmessage"`**

When using `@react-oauth/google` with `flow: 'auth-code'`, the library uses Google's
popup mode which sets `redirect_uri=postmessage`. The Django backend MUST use the same
value as `callback_url`, otherwise Google will return a `redirect_uri_mismatch` error
during the code-to-token exchange.

### URL Configuration

```python
# In urls.py
path("api/auth/google/", GoogleLogin.as_view(), name="google-login"),
```

### What Happens Internally

1. `SocialLoginView` receives the `code`
2. It uses `OAuth2Client` + `GoogleOAuth2Adapter` to exchange the code with Google
3. Google returns access_token + id_token
4. allauth's `SocialLoginView` creates or retrieves the Django user
5. dj-rest-auth generates JWT access + refresh tokens
6. Tokens are returned in the response body AND as Set-Cookie headers (when configured)

---

## 3. JWT Token Storage Best Practices

### 2025-2026 Consensus

| Storage Method    | XSS Safe | CSRF Safe | Survives Refresh | Recommendation       |
|-------------------|----------|-----------|------------------|----------------------|
| localStorage      | No       | Yes       | Yes              | Not recommended      |
| sessionStorage    | No       | Yes       | No               | Not recommended      |
| In-memory only    | Yes      | Yes       | No               | Good for access token|
| httpOnly cookie   | Yes      | No*       | Yes              | Best for refresh     |

*CSRF must be mitigated separately when using cookies.

### Recommended Hybrid Approach

The current best practice is:

- **Access token**: Stored in an httpOnly cookie (dj-rest-auth handles this automatically)
- **Refresh token**: Stored in an httpOnly cookie (dj-rest-auth handles this automatically)
- **CSRF protection**: Use `SameSite=Lax` + CSRF token for state-changing requests

This is simpler than the "access token in memory, refresh token in cookie" pattern because
dj-rest-auth natively supports setting both tokens as httpOnly cookies. The browser
automatically sends them with every request when `withCredentials: true` is set.

### dj-rest-auth JWT Cookie Settings

```python
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access_token",           # Cookie name for access token
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",  # Cookie name for refresh token
    "JWT_AUTH_HTTPONLY": True,                    # JS cannot read tokens (default)
    "JWT_AUTH_SECURE": False,                    # True in production (HTTPS only)
    "JWT_AUTH_SAMESITE": "Lax",                  # Prevents CSRF in most cases
    "JWT_AUTH_COOKIE_USE_CSRF": True,            # Enable CSRF for cookie-auth views
    "JWT_AUTH_RETURN_EXPIRATION": True,           # Return expiry in response body
}
```

### Important: JWT_AUTH_HTTPONLY and Token Refresh

When `JWT_AUTH_HTTPONLY=True`, the refresh token is stored in an httpOnly cookie. The
dj-rest-auth `/token/refresh/` endpoint reads the refresh token from the cookie
automatically -- JS does not need to access it. This is the secure default.

However, there is a known issue (dj-rest-auth #571): if `JWT_AUTH_HTTPONLY=True`, the
refresh token body in login response is empty string. The refresh endpoint still works
because it reads from the cookie, but this can be confusing.

---

## 4. React Google OAuth Integration

### Recommendation: `@react-oauth/google`

**Use `@react-oauth/google`** (MIT license, 1.2M+ weekly downloads on npm) for the
Google sign-in button. It wraps Google Identity Services SDK and provides React hooks.

### Why `@react-oauth/google` over redirect flow:

| Aspect                | @react-oauth/google (popup) | Redirect through Django |
|-----------------------|-----------------------------|-------------------------|
| UX                    | Popup, SPA stays loaded     | Full page redirect      |
| Complexity            | Moderate                    | Lower                   |
| SPA state preserved   | Yes                         | No (page reloads)       |
| Google branding       | Built-in                    | Manual                  |
| Token exchange        | Frontend gets code, POSTs   | Django handles all      |

### Implementation

```bash
npm install @react-oauth/google
```

Wrap the app with `GoogleOAuthProvider`:

```tsx
// main.tsx or App.tsx
import { GoogleOAuthProvider } from '@react-oauth/google';

<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
  <App />
</GoogleOAuthProvider>
```

Use the `useGoogleLogin` hook with `flow: 'auth-code'`:

```tsx
import { useGoogleLogin } from '@react-oauth/google';

const login = useGoogleLogin({
  onSuccess: async (codeResponse) => {
    // POST the authorization code to Django backend
    const res = await api.post('/auth/google/', {
      code: codeResponse.code,
    });
    // On success, JWT cookies are set automatically by the browser
    // Fetch the user profile
    const userRes = await api.get('/accounts/me/');
    setUser(userRes.data);
  },
  onError: (error) => {
    console.error('Google login failed:', error);
  },
  flow: 'auth-code',
});
```

---

## 5. CORS and Cookie Configuration

### Required Django Settings for Cookie-Based Auth

```python
# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",   # Alternative dev port
]
CORS_ALLOW_CREDENTIALS = True  # REQUIRED for cookies to be sent cross-origin

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# Cookie settings for development
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# For production (HTTPS):
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
```

### Key Points

- `CORS_ALLOW_CREDENTIALS = True` is mandatory for browsers to send/receive cookies
  cross-origin. When enabled, `CORS_ALLOW_ALL_ORIGINS` must NOT be `True`.
- `withCredentials: true` must be set on the Axios client (already done in `api.ts`).
- `SameSite=Lax` works when frontend and backend share the same top-level domain.
  For `localhost` with different ports, `Lax` works in most browsers.
- In production with separate domains (e.g., `app.toledot.com` and `api.toledot.com`),
  use `SameSite=None; Secure` and ensure HTTPS.

---

## 6. Token Refresh Strategy

### How It Works with httpOnly Cookies

1. On login, dj-rest-auth sets `access_token` and `refresh_token` as httpOnly cookies
2. Every API request automatically includes these cookies (browser handles this)
3. When access token expires (30 min), API returns 401
4. Frontend calls `POST /api/auth/token/refresh/` (no body needed -- cookie is sent automatically)
5. Server reads refresh token from cookie, issues new access token, sets new cookie

### Frontend Token Refresh Flow

```tsx
// In api.ts interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // No body needed - refresh token is in httpOnly cookie
        await api.post('/auth/token/refresh/');
        // Retry the original request (new access token cookie is set)
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);
```

### On Page Reload

When the page reloads, the SPA loses in-memory state but cookies persist. The app should:

1. On mount, call `GET /api/accounts/me/` (cookies sent automatically)
2. If 200: user is authenticated, populate the auth store
3. If 401: attempt token refresh, then retry
4. If refresh also fails: redirect to login

---

## 7. Code Examples

### Backend: Complete Settings Addition

```python
# backend/config/settings/base.py - additions to existing REST_AUTH

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "JWT_AUTH_HTTPONLY": True,
    "JWT_AUTH_SECURE": False,               # True in production
    "JWT_AUTH_SAMESITE": "Lax",
    "JWT_AUTH_COOKIE_USE_CSRF": True,
    "JWT_AUTH_RETURN_EXPIRATION": True,
}

CORS_ALLOW_CREDENTIALS = True
```

### Backend: Google Login View

```python
# apps/accounts/views.py
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "postmessage"
    client_class = OAuth2Client
```

### Backend: URL Configuration

```python
# apps/accounts/urls.py (add to existing)
from apps.accounts.views import GoogleLogin

urlpatterns = [
    # ... existing patterns ...
    path("google/", GoogleLogin.as_view(), name="google-login"),
]
```

Or at the project level:

```python
# config/urls.py (add)
path("api/auth/google/", GoogleLogin.as_view(), name="google-login"),
```

### Frontend: GoogleOAuthProvider Setup

```tsx
// frontend/src/main.tsx
import { GoogleOAuthProvider } from '@react-oauth/google';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
);
```

### Frontend: LoginPage with Google OAuth

```tsx
// frontend/src/pages/LoginPage.tsx
import { useGoogleLogin } from '@react-oauth/google';
import api from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

export function LoginPage() {
  const { setUser, setLoading } = useAuthStore();

  const googleLogin = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        setLoading(true);
        // Send auth code to backend
        await api.post('/auth/google/', {
          code: codeResponse.code,
        });
        // Fetch user profile (JWT cookie is now set)
        const userRes = await api.get('/accounts/me/');
        setUser(userRes.data);
        // Navigate to dashboard
        window.location.href = '/';
      } catch (error) {
        console.error('Login failed:', error);
        setLoading(false);
      }
    },
    onError: () => {
      console.error('Google login failed');
    },
    flow: 'auth-code',
  });

  return (
    <div>
      {/* ... existing UI ... */}
      <button onClick={() => googleLogin()}>
        Sign in with Google
      </button>
    </div>
  );
}
```

### Frontend: Auth Store with Initialization

```tsx
// frontend/src/stores/authStore.ts
import { create } from 'zustand';
import api from '@/services/api';
import type { User } from '@/types';

type AuthState = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  initialize: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),
  setLoading: (isLoading) => set({ isLoading }),
  logout: async () => {
    try {
      await api.post('/auth/logout/');
    } catch {
      // Ignore logout errors
    }
    set({ user: null, isAuthenticated: false, isLoading: false });
  },
  initialize: async () => {
    try {
      const res = await api.get('/accounts/me/');
      set({ user: res.data, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
```

### Frontend: Axios Interceptor with Silent Refresh

```tsx
// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: unknown | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => api(originalRequest));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await api.post('/auth/token/refresh/');
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default api;
```

---

## 8. Recommended Architecture for Toledot

### Summary of Decisions

| Decision                    | Choice                                      | Rationale                                          |
|-----------------------------|---------------------------------------------|----------------------------------------------------|
| OAuth flow                  | Authorization Code (popup)                  | Secure, good UX, no page reload                    |
| Frontend library            | `@react-oauth/google` (MIT)                | Most popular, well-maintained, Google SDK wrapper   |
| Backend endpoint            | `SocialLoginView` + `callback_url="postmessage"` | Works with popup flow                        |
| Token storage               | httpOnly cookies (both access + refresh)    | dj-rest-auth native support, XSS-safe              |
| Token refresh               | 401 interceptor + silent refresh            | Transparent to user                                |
| CSRF protection             | `SameSite=Lax` + `JWT_AUTH_COOKIE_USE_CSRF` | Defense in depth                                  |
| Session initialization      | `GET /api/accounts/me/` on app mount        | Cookies persist across page reloads                |

### Implementation Checklist

Backend:
- [ ] Add `GoogleLogin` view with `callback_url="postmessage"`
- [ ] Wire up `POST /api/auth/google/` URL
- [ ] Update `REST_AUTH` with cookie settings (cookie names, httpOnly, CSRF)
- [ ] Add `CORS_ALLOW_CREDENTIALS = True`
- [ ] Add `CSRF_TRUSTED_ORIGINS`
- [ ] Ensure `/api/accounts/me/` endpoint exists and returns user profile

Frontend:
- [ ] Install `@react-oauth/google`
- [ ] Wrap app with `GoogleOAuthProvider`
- [ ] Update `LoginPage` to use `useGoogleLogin` with `flow: 'auth-code'`
- [ ] Add token refresh interceptor to Axios
- [ ] Add `initialize()` to auth store for session recovery on page load
- [ ] Call `initialize()` in app root / layout component

Google Cloud Console:
- [ ] Add `http://localhost:5173` to Authorized JavaScript Origins
- [ ] No redirect URI needed for popup flow (uses `postmessage`)
