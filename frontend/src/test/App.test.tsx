import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../App";
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

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it("renders without crashing", () => {
    vi.mocked(api.fetchCurrentUser).mockRejectedValue(new Error("Not authenticated"));
    render(<App />);
    expect(document.getElementById("root") || document.body).toBeTruthy();
  });

  it("renders the home page with welcome text when authenticated", async () => {
    const mockUser = {
      id: "1",
      email: "test@example.com",
      displayName: "Test User",
      avatarUrl: null,
      createdAt: "2024-01-01T00:00:00Z",
    };

    useAuthStore.setState({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
    });

    vi.mocked(api.fetchCurrentUser).mockResolvedValue(mockUser);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Welcome to Toledot")).toBeInTheDocument();
    });
  });

  it("renders navigation links when authenticated", async () => {
    const mockUser = {
      id: "1",
      email: "test@example.com",
      displayName: "Test User",
      avatarUrl: null,
      createdAt: "2024-01-01T00:00:00Z",
    };

    useAuthStore.setState({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
    });

    vi.mocked(api.fetchCurrentUser).mockResolvedValue(mockUser);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Home")).toBeInTheDocument();
      expect(screen.getByText("Eras")).toBeInTheDocument();
      expect(screen.getByText("Chat")).toBeInTheDocument();
    });
  });
});
