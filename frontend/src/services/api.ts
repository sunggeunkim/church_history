import axios from "axios";
import type { User, Era, KeyEvent, KeyFigure } from "@/types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// CSRF token handling
let csrfToken: string | null = null;

export async function fetchCsrfToken(): Promise<void> {
  try {
    const response = await api.get("/auth/csrf/");
    csrfToken = response.data.csrfToken;
    if (csrfToken) {
      api.defaults.headers.common["X-CSRFToken"] = csrfToken;
    }
  } catch (error) {
    console.error("Failed to fetch CSRF token:", error);
  }
}

// Auth API functions
export async function googleLogin(code: string): Promise<void> {
  await api.post("/auth/google/", { code });
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await api.get("/accounts/me/");
  // Map snake_case from backend to camelCase for frontend
  const data = response.data;
  return {
    id: data.id,
    email: data.email,
    displayName: data.display_name,
    avatarUrl: data.avatar_url,
    createdAt: data.date_joined,
  };
}

export async function logout(): Promise<void> {
  await api.post("/accounts/logout/");
}

export async function refreshToken(): Promise<void> {
  await api.post("/auth/token/refresh/");
}

// Response interceptor with token refresh logic
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null = null) => {
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
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await refreshToken();
        processQueue();
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as Error);
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

// Era API functions
function mapKeyEvent(data: any): KeyEvent {
  return {
    id: data.id,
    year: data.year,
    title: data.title,
    description: data.description,
  };
}

function mapKeyFigure(data: any): KeyFigure {
  return {
    id: data.id,
    name: data.name,
    birthYear: data.birth_year,
    deathYear: data.death_year,
    title: data.title,
    description: data.description,
  };
}

function mapEra(data: any): Era {
  return {
    id: data.id,
    name: data.name,
    slug: data.slug,
    startYear: data.start_year,
    endYear: data.end_year,
    description: data.description,
    summary: data.summary,
    color: data.color,
    order: data.order,
    keyEvents: data.key_events?.map(mapKeyEvent),
    keyFigures: data.key_figures?.map(mapKeyFigure),
  };
}

export async function fetchEras(): Promise<Era[]> {
  const response = await api.get("/eras/");
  return response.data.results.map(mapEra);
}

export async function fetchEra(slug: string): Promise<Era> {
  const response = await api.get(`/eras/${slug}/`);
  return mapEra(response.data);
}

export async function fetchTimeline(): Promise<Era[]> {
  const response = await api.get("/eras/timeline/");
  return response.data.map(mapEra);
}

export default api;
