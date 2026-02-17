import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { LoginPage } from "../pages/LoginPage";

describe("LoginPage", () => {
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
