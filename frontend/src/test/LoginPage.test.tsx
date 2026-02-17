import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LoginPage } from "../pages/LoginPage";
import { useAuthStore } from "@/stores/authStore";

// Mock the Google OAuth library
vi.mock("@react-oauth/google", () => ({
  useGoogleLogin: () => vi.fn(),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it("renders the sign-in page", () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    );
    expect(screen.getByText("Sign in with Google")).toBeInTheDocument();
    expect(screen.getByText("Welcome back.")).toBeInTheDocument();
  });

  it("displays the app name", () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    );
    expect(screen.getByText("Toledot")).toBeInTheDocument();
  });
});
