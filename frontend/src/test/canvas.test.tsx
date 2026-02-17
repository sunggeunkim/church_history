import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import type { Era } from "@/types";

// Mock the stores before importing components
vi.mock("@/stores/eraStore", () => {
  const create = vi.fn(() => vi.fn());
  return {
    useEraStore: vi.fn(),
    __esModule: true,
  };
});

vi.mock("@/stores/chatStore", () => ({
  useChatStore: vi.fn(),
}));

vi.mock("@/hooks/useMediaQuery", () => ({
  useMediaQuery: vi.fn(() => true),
}));

import { useEraStore } from "@/stores/eraStore";
import { useChatStore } from "@/stores/chatStore";
import { useMediaQuery } from "@/hooks/useMediaQuery";

const mockEras: Era[] = [
  {
    id: 1,
    name: "Early Church",
    slug: "early-church",
    startYear: 30,
    endYear: 325,
    description: "The apostolic age and early Christianity.",
    summary: "From Pentecost to the Council of Nicaea.",
    color: "#C2410C",
    order: 1,
    keyEvents: [
      {
        id: 1,
        year: 30,
        title: "Pentecost",
        description: "The Holy Spirit descends.",
      },
      {
        id: 2,
        year: 70,
        title: "Fall of Jerusalem",
        description: "The Temple is destroyed.",
      },
    ],
    keyFigures: [
      {
        id: 1,
        name: "Apostle Paul",
        birthYear: 5,
        deathYear: 67,
        title: "Apostle to the Gentiles",
        description: "Missionary and author.",
      },
    ],
  },
  {
    id: 2,
    name: "Nicene Era",
    slug: "nicene-era",
    startYear: 325,
    endYear: 590,
    description: "The age of creeds and councils.",
    summary: "From Nicaea to Gregory the Great.",
    color: "#7C3AED",
    order: 2,
    keyEvents: [],
    keyFigures: [],
  },
];

const defaultEraStore = {
  timelineData: mockEras,
  isLoadingTimeline: false,
  expandedEraId: null,
  error: null,
  fetchTimeline: vi.fn(),
  toggleExpanded: vi.fn(),
  setExpandedEra: vi.fn(),
  eras: mockEras,
  selectedEra: null,
  isLoading: false,
  fetchEras: vi.fn(),
  fetchEra: vi.fn(),
  selectEra: vi.fn(),
};

const defaultChatStore = {
  sessions: [],
  activeSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: "",
  isLoadingSessions: false,
  isLoadingMessages: false,
  error: null,
  loadSessions: vi.fn(),
  createSession: vi.fn(),
  deleteSession: vi.fn(),
  setActiveSession: vi.fn(),
  loadMessages: vi.fn(),
  sendMessage: vi.fn(),
  cancelStream: vi.fn(),
  clearError: vi.fn(),
};

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("Canvas Components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useEraStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      defaultEraStore,
    );
    (useChatStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      defaultChatStore,
    );
    (useMediaQuery as unknown as ReturnType<typeof vi.fn>).mockReturnValue(true);
  });

  describe("CanvasOverviewBar", () => {
    it("renders all eras as buttons", async () => {
      const { CanvasOverviewBar } = await import(
        "@/components/canvas/CanvasOverviewBar"
      );
      render(
        <CanvasOverviewBar
          eras={mockEras}
          selectedEraId={null}
          onEraClick={vi.fn()}
        />,
      );

      expect(
        screen.getByRole("tab", { name: /navigate to early church/i }),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("tab", { name: /navigate to nicene era/i }),
      ).toBeInTheDocument();
    });

    it("calls onEraClick when a segment is clicked", async () => {
      const { CanvasOverviewBar } = await import(
        "@/components/canvas/CanvasOverviewBar"
      );
      const onEraClick = vi.fn();
      render(
        <CanvasOverviewBar
          eras={mockEras}
          selectedEraId={null}
          onEraClick={onEraClick}
        />,
      );

      await userEvent.click(
        screen.getByRole("tab", { name: /navigate to early church/i }),
      );
      expect(onEraClick).toHaveBeenCalledWith(mockEras[0]);
    });

    it("marks selected era with aria-selected", async () => {
      const { CanvasOverviewBar } = await import(
        "@/components/canvas/CanvasOverviewBar"
      );
      render(
        <CanvasOverviewBar
          eras={mockEras}
          selectedEraId={1}
          onEraClick={vi.fn()}
        />,
      );

      const selectedTab = screen.getByRole("tab", {
        name: /navigate to early church/i,
      });
      expect(selectedTab).toHaveAttribute("aria-selected", "true");
    });
  });

  describe("CanvasEraBlock", () => {
    it("renders era name and years", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={false}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText("30–325")).toBeInTheDocument();
    });

    it("shows summary when collapsed", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={false}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(
        screen.getByText("From Pentecost to the Council of Nicaea."),
      ).toBeInTheDocument();
    });

    it("shows events and figures when expanded", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={true}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(screen.getByText("Pentecost")).toBeInTheDocument();
      expect(screen.getByText("Fall of Jerusalem")).toBeInTheDocument();
      expect(screen.getByText("Apostle Paul")).toBeInTheDocument();
    });

    it("shows chat button when expanded", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={true}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(
        screen.getByRole("button", { name: /chat about this era/i }),
      ).toBeInTheDocument();
    });

    it("calls onToggle when header is clicked", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      const onToggle = vi.fn();
      render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={false}
          isSelected={false}
          onToggle={onToggle}
          onChatClick={vi.fn()}
        />,
      );

      await userEvent.click(
        screen.getByRole("button", { name: /expand early church/i }),
      );
      expect(onToggle).toHaveBeenCalled();
    });

    it("calls onChatClick when chat button is clicked", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      const onChatClick = vi.fn();
      render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={true}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={onChatClick}
        />,
      );

      await userEvent.click(
        screen.getByRole("button", { name: /chat about this era/i }),
      );
      expect(onChatClick).toHaveBeenCalled();
    });

    it("shows aria-expanded attribute", async () => {
      const { CanvasEraBlock } = await import(
        "@/components/canvas/CanvasEraBlock"
      );
      const { rerender } = render(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={false}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(
        screen.getByRole("button", { name: /expand early church/i }),
      ).toHaveAttribute("aria-expanded", "false");

      rerender(
        <CanvasEraBlock
          era={mockEras[0]}
          isExpanded={true}
          isSelected={false}
          onToggle={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(
        screen.getByRole("button", { name: /collapse early church/i }),
      ).toHaveAttribute("aria-expanded", "true");
    });
  });

  describe("CanvasEventList", () => {
    it("renders events sorted by year", async () => {
      const { CanvasEventList } = await import(
        "@/components/canvas/CanvasEventList"
      );
      render(
        <CanvasEventList
          events={mockEras[0].keyEvents!}
          accentColor="#C2410C"
        />,
      );

      expect(screen.getByText("Pentecost")).toBeInTheDocument();
      expect(screen.getByText("Fall of Jerusalem")).toBeInTheDocument();
      expect(screen.getByText("30")).toBeInTheDocument();
      expect(screen.getByText("70")).toBeInTheDocument();
    });

    it("returns null for empty events", async () => {
      const { CanvasEventList } = await import(
        "@/components/canvas/CanvasEventList"
      );
      const { container } = render(
        <CanvasEventList events={[]} accentColor="#C2410C" />,
      );
      expect(container.firstChild).toBeNull();
    });
  });

  describe("CanvasFigureList", () => {
    it("renders figures with names and years", async () => {
      const { CanvasFigureList } = await import(
        "@/components/canvas/CanvasFigureList"
      );
      render(
        <CanvasFigureList
          figures={mockEras[0].keyFigures!}
          accentColor="#C2410C"
        />,
      );

      expect(screen.getByText("Apostle Paul")).toBeInTheDocument();
      expect(screen.getByText("5–67")).toBeInTheDocument();
      expect(screen.getByText("Apostle to the Gentiles")).toBeInTheDocument();
    });

    it("returns null for empty figures", async () => {
      const { CanvasFigureList } = await import(
        "@/components/canvas/CanvasFigureList"
      );
      const { container } = render(
        <CanvasFigureList figures={[]} accentColor="#C2410C" />,
      );
      expect(container.firstChild).toBeNull();
    });
  });

  describe("CanvasChatPanel", () => {
    it("shows empty state when no era is selected", async () => {
      const { CanvasChatPanel } = await import(
        "@/components/canvas/CanvasChatPanel"
      );
      render(<CanvasChatPanel selectedEra={null} />);

      expect(screen.getByText("Select an Era")).toBeInTheDocument();
    });

    it("shows start chat button when era selected but no session", async () => {
      const { CanvasChatPanel } = await import(
        "@/components/canvas/CanvasChatPanel"
      );
      render(<CanvasChatPanel selectedEra={mockEras[0]} />);

      expect(
        screen.getByRole("button", { name: /start chatting/i }),
      ).toBeInTheDocument();
    });

    it("shows era header with name and years", async () => {
      const { CanvasChatPanel } = await import(
        "@/components/canvas/CanvasChatPanel"
      );
      render(<CanvasChatPanel selectedEra={mockEras[0]} />);

      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText("30–325")).toBeInTheDocument();
    });

    it("calls createSession when start chat is clicked", async () => {
      const { CanvasChatPanel } = await import(
        "@/components/canvas/CanvasChatPanel"
      );
      const createSession = vi.fn().mockResolvedValue({ id: "1" });
      (useChatStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultChatStore,
        createSession,
      });

      render(<CanvasChatPanel selectedEra={mockEras[0]} />);

      await userEvent.click(
        screen.getByRole("button", { name: /start chatting/i }),
      );
      expect(createSession).toHaveBeenCalledWith("1");
    });
  });

  describe("CanvasTimeline", () => {
    it("renders era blocks for all eras", async () => {
      const { CanvasTimeline } = await import(
        "@/components/canvas/CanvasTimeline"
      );
      render(
        <CanvasTimeline
          eras={mockEras}
          expandedEraId={null}
          selectedEraId={null}
          onToggleExpand={vi.fn()}
          onChatClick={vi.fn()}
        />,
      );

      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText("Nicene Era")).toBeInTheDocument();
    });
  });

  describe("CanvasPage", () => {
    it("renders loading state", async () => {
      (useEraStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultEraStore,
        timelineData: null,
        isLoadingTimeline: true,
      });

      const { CanvasPage } = await import("@/pages/CanvasPage");
      renderWithRouter(<CanvasPage />);

      expect(screen.getByText("Loading timeline...")).toBeInTheDocument();
    });

    it("renders error state", async () => {
      (useEraStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultEraStore,
        timelineData: null,
        error: "Network error",
      });

      const { CanvasPage } = await import("@/pages/CanvasPage");
      renderWithRouter(<CanvasPage />);

      expect(screen.getByText("Network error")).toBeInTheDocument();
    });

    it("renders overview bar and timeline when data loaded", async () => {
      const { CanvasPage } = await import("@/pages/CanvasPage");
      renderWithRouter(<CanvasPage />);

      expect(screen.getAllByText("Early Church").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("Nicene Era").length).toBeGreaterThanOrEqual(1);
    });

    it("calls fetchTimeline on mount", async () => {
      const fetchTimeline = vi.fn();
      (useEraStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultEraStore,
        fetchTimeline,
      });

      const { CanvasPage } = await import("@/pages/CanvasPage");
      renderWithRouter(<CanvasPage />);

      expect(fetchTimeline).toHaveBeenCalled();
    });
  });
});
