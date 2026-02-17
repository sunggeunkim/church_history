import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LoginPage } from "@/pages/LoginPage";
import { useAuthStore } from "@/stores/authStore";
import * as api from "@/services/api";

// Mock the API module
vi.mock("@/services/api", () => ({
  fetchCsrfToken: vi.fn().mockResolvedValue(undefined),
  fetchCurrentUser: vi.fn(),
  googleLogin: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Mock the Google OAuth library
vi.mock("@react-oauth/google", () => ({
  GoogleOAuthProvider: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  useGoogleLogin: () => vi.fn(),
}));

describe("AuthProvider", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
    });
  });

  it("renders loading state initially", () => {
    render(
      <AuthProvider>
        <div>Test Content</div>
      </AuthProvider>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(screen.queryByText("Test Content")).not.toBeInTheDocument();
  });

  it("renders children after loading completes", async () => {
    vi.mocked(api.fetchCurrentUser).mockRejectedValue(new Error("Not authenticated"));

    render(
      <AuthProvider>
        <div>Test Content</div>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Test Content")).toBeInTheDocument();
    });
  });

  it("fetches CSRF token on mount", async () => {
    vi.mocked(api.fetchCurrentUser).mockRejectedValue(new Error("Not authenticated"));

    render(
      <AuthProvider>
        <div>Test Content</div>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(api.fetchCsrfToken).toHaveBeenCalled();
    });
  });
});

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("redirects to login when not authenticated", () => {
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });

    render(
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<div>Protected Content</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    );

    expect(screen.getByText("Login Page")).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  it("renders content when authenticated", async () => {
    // Mock the store with authenticated state
    useAuthStore.setState({
      user: {
        id: "1",
        email: "test@example.com",
        displayName: "Test User",
        avatarUrl: null,
        createdAt: "2024-01-01T00:00:00Z",
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<div>Protected Content</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    );

    // ProtectedRoute renders Outlet when authenticated
    await waitFor(() => {
      expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });
  });

  it("shows loading spinner while checking authentication", () => {
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
    });

    render(<ProtectedRoute />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });
});

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it("renders Google sign-in button", () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    expect(screen.getByText("Sign in with Google")).toBeInTheDocument();
    expect(screen.getByText("Toledot")).toBeInTheDocument();
    expect(screen.getByText("Welcome back.")).toBeInTheDocument();
  });

  it("redirects to home if already authenticated", () => {
    useAuthStore.setState({
      user: {
        id: "1",
        email: "test@example.com",
        displayName: "Test User",
        avatarUrl: null,
        createdAt: "2024-01-01T00:00:00Z",
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<div>Home Page</div>} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    );

    expect(screen.getByText("Home Page")).toBeInTheDocument();
  });
});

describe("authStore", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
    });
  });

  it("sets user on successful checkAuth", async () => {
    const mockUser = {
      id: "1",
      email: "test@example.com",
      displayName: "Test User",
      avatarUrl: null,
      createdAt: "2024-01-01T00:00:00Z",
    };

    vi.mocked(api.fetchCurrentUser).mockResolvedValue(mockUser);

    await useAuthStore.getState().checkAuth();

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
    expect(state.isLoading).toBe(false);
  });

  it("clears user on failed checkAuth", async () => {
    vi.mocked(api.fetchCurrentUser).mockRejectedValue(new Error("Unauthorized"));

    await useAuthStore.getState().checkAuth();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });

  it("handles Google login flow", async () => {
    const mockUser = {
      id: "1",
      email: "test@example.com",
      displayName: "Test User",
      avatarUrl: null,
      createdAt: "2024-01-01T00:00:00Z",
    };

    vi.mocked(api.googleLogin).mockResolvedValue(undefined);
    vi.mocked(api.fetchCurrentUser).mockResolvedValue(mockUser);

    await useAuthStore.getState().loginWithGoogle("test-code");

    expect(api.googleLogin).toHaveBeenCalledWith("test-code");
    expect(api.fetchCurrentUser).toHaveBeenCalled();

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it("handles logout", async () => {
    useAuthStore.setState({
      user: {
        id: "1",
        email: "test@example.com",
        displayName: "Test User",
        avatarUrl: null,
        createdAt: "2024-01-01T00:00:00Z",
      },
      isAuthenticated: true,
      isLoading: false,
    });

    vi.mocked(api.logout).mockResolvedValue(undefined);

    // Mock window.location.href
    const originalHref = window.location.href;
    Object.defineProperty(window, "location", {
      writable: true,
      value: { ...window.location, href: "" },
    });

    await useAuthStore.getState().performLogout();

    expect(api.logout).toHaveBeenCalled();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);

    // Restore window.location.href
    Object.defineProperty(window, "location", {
      writable: true,
      value: { ...window.location, href: originalHref },
    });
  });
});
