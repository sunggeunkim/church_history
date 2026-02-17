import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { ErasPage } from "@/pages/ErasPage";
import { Timeline } from "@/components/eras/Timeline";
import { EraCard } from "@/components/eras/EraCard";
import { useEraStore } from "@/stores/eraStore";
import type { Era } from "@/types";

// Mock the era store
vi.mock("@/stores/eraStore");

const mockEras: Era[] = [
  {
    id: 1,
    name: "Early Church",
    slug: "early-church",
    startYear: 30,
    endYear: 325,
    description: "The period from Pentecost to the Council of Nicaea.",
    summary: "Formation of Christian doctrine and practice",
    color: "#C2410C",
    order: 1,
    keyEvents: [
      {
        id: 1,
        year: 30,
        title: "Pentecost",
        description: "Birth of the Church",
      },
    ],
    keyFigures: [
      {
        id: 1,
        name: "Augustine",
        birthYear: 354,
        deathYear: 430,
        title: "Bishop of Hippo",
        description: "Influential theologian",
      },
    ],
  },
  {
    id: 2,
    name: "Nicene & Post-Nicene",
    slug: "nicene-post-nicene",
    startYear: 325,
    endYear: 590,
    description: "The period of great ecumenical councils.",
    summary: "Development of Trinitarian theology",
    color: "#B45309",
    order: 2,
    keyEvents: [],
    keyFigures: [],
  },
];

describe("ErasPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders era cards when data is loaded", async () => {
    const mockFetchEras = vi.fn();
    const mockSelectEra = vi.fn();

    vi.mocked(useEraStore).mockReturnValue({
      eras: mockEras,
      selectedEra: null,
      isLoading: false,
      error: null,
      fetchEras: mockFetchEras,
      fetchEra: vi.fn(),
      selectEra: mockSelectEra,
    });

    render(
      <BrowserRouter>
        <ErasPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText("Nicene & Post-Nicene")).toBeInTheDocument();
    });

    expect(mockFetchEras).toHaveBeenCalledOnce();
  });

  it("shows loading state", () => {
    vi.mocked(useEraStore).mockReturnValue({
      eras: [],
      selectedEra: null,
      isLoading: true,
      error: null,
      fetchEras: vi.fn(),
      fetchEra: vi.fn(),
      selectEra: vi.fn(),
    });

    render(
      <BrowserRouter>
        <ErasPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading eras/i)).toBeInTheDocument();
  });

  it("shows error state", () => {
    vi.mocked(useEraStore).mockReturnValue({
      eras: [],
      selectedEra: null,
      isLoading: false,
      error: "Failed to fetch eras",
      fetchEras: vi.fn(),
      fetchEra: vi.fn(),
      selectEra: vi.fn(),
    });

    render(
      <BrowserRouter>
        <ErasPage />
      </BrowserRouter>
    );

    expect(screen.getByText("Failed to fetch eras")).toBeInTheDocument();
  });

  it("displays selected era details when an era is selected", () => {
    vi.mocked(useEraStore).mockReturnValue({
      eras: mockEras,
      selectedEra: mockEras[0],
      isLoading: false,
      error: null,
      fetchEras: vi.fn(),
      fetchEra: vi.fn(),
      selectEra: vi.fn(),
    });

    render(
      <BrowserRouter>
        <ErasPage />
      </BrowserRouter>
    );

    expect(
      screen.getByText("The period from Pentecost to the Council of Nicaea.")
    ).toBeInTheDocument();
    expect(screen.getByText("Key Events")).toBeInTheDocument();
    expect(screen.getByText("Key Figures")).toBeInTheDocument();
  });
});

describe("Timeline", () => {
  it("renders timeline with all eras", () => {
    const mockOnEraClick = vi.fn();

    render(
      <Timeline
        eras={mockEras}
        selectedEra={null}
        onEraClick={mockOnEraClick}
      />
    );

    expect(screen.getByText("Early Church")).toBeInTheDocument();
    expect(screen.getByText("Nicene & Post-Nicene")).toBeInTheDocument();
    expect(screen.getByText("30–325")).toBeInTheDocument();
    expect(screen.getByText("325–590")).toBeInTheDocument();
  });

  it("calls onEraClick when an era is clicked", async () => {
    const user = userEvent.setup();
    const mockOnEraClick = vi.fn();

    render(
      <Timeline
        eras={mockEras}
        selectedEra={null}
        onEraClick={mockOnEraClick}
      />
    );

    const eraButton = screen.getByLabelText("Select Early Church era");
    await user.click(eraButton);

    expect(mockOnEraClick).toHaveBeenCalledWith(mockEras[0]);
  });
});

describe("EraCard", () => {
  it("renders era information", () => {
    const mockNavigate = vi.fn();
    vi.mock("react-router-dom", async () => {
      const actual = await vi.importActual("react-router-dom");
      return {
        ...actual,
        useNavigate: () => mockNavigate,
      };
    });

    render(
      <BrowserRouter>
        <EraCard era={mockEras[0]} />
      </BrowserRouter>
    );

    expect(screen.getByText("Early Church")).toBeInTheDocument();
    expect(screen.getByText("30–325")).toBeInTheDocument();
    expect(
      screen.getByText("Formation of Christian doctrine and practice")
    ).toBeInTheDocument();
  });

  it("calls onClick when clicked", async () => {
    const user = userEvent.setup();
    const mockOnClick = vi.fn();

    render(
      <BrowserRouter>
        <EraCard era={mockEras[0]} onClick={mockOnClick} />
      </BrowserRouter>
    );

    const card = screen.getByRole("button");
    await user.click(card);

    expect(mockOnClick).toHaveBeenCalled();
  });
});

describe("Era Store", () => {
  it("transitions from loading to loaded state", () => {
    const initialState = {
      eras: [],
      selectedEra: null,
      isLoading: true,
      error: null,
    };

    const loadedState = {
      eras: mockEras,
      selectedEra: null,
      isLoading: false,
      error: null,
    };

    expect(initialState.isLoading).toBe(true);
    expect(initialState.eras).toHaveLength(0);

    expect(loadedState.isLoading).toBe(false);
    expect(loadedState.eras).toHaveLength(2);
  });

  it("handles error state", () => {
    const errorState = {
      eras: [],
      selectedEra: null,
      isLoading: false,
      error: "Failed to fetch eras",
    };

    expect(errorState.error).toBe("Failed to fetch eras");
    expect(errorState.eras).toHaveLength(0);
  });

  it("updates selected era", () => {
    const state = {
      eras: mockEras,
      selectedEra: null,
      isLoading: false,
      error: null,
    };

    const updatedState = {
      ...state,
      selectedEra: mockEras[0],
    };

    expect(updatedState.selectedEra).toBe(mockEras[0]);
  });
});
