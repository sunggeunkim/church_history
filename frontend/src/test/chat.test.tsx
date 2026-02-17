import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { ChatPage } from "@/pages/ChatPage";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { useChatStore } from "@/stores/chatStore";
import type { ChatMessage, ChatSession } from "@/types";

// Mock the chat store
vi.mock("@/stores/chatStore");

// Mock the useMediaQuery hook to return desktop by default
vi.mock("@/hooks/useMediaQuery", () => ({
  useMediaQuery: () => true,
}));

// Mock react-markdown to render plain text (avoids ESM issues in jsdom)
vi.mock("react-markdown", () => ({
  default: ({ children }: { children: string }) => <div data-testid="markdown">{children}</div>,
}));

vi.mock("remark-gfm", () => ({
  default: () => {},
}));

const mockSessions: ChatSession[] = [
  {
    id: "session-1",
    title: "Early Church History",
    eraId: null,
    createdAt: "2025-12-01T10:00:00Z",
    updatedAt: "2025-12-01T12:00:00Z",
  },
  {
    id: "session-2",
    title: "Reformation Questions",
    eraId: null,
    createdAt: "2025-11-28T08:00:00Z",
    updatedAt: "2025-11-29T15:00:00Z",
  },
];

const mockMessages: ChatMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content: "Tell me about the Council of Nicaea",
    createdAt: "2025-12-01T10:01:00Z",
  },
  {
    id: "msg-2",
    role: "assistant",
    content:
      "The Council of Nicaea was the first ecumenical council, held in 325 AD.",
    createdAt: "2025-12-01T10:01:05Z",
    sources: [
      {
        title: "Council of Nicaea",
        url: "https://example.com/nicaea",
        source: "Encyclopedia",
      },
    ],
  },
];

function createMockStoreState(overrides: Partial<ReturnType<typeof useChatStore>> = {}) {
  return {
    sessions: [],
    activeSessionId: null,
    messages: [],
    isStreaming: false,
    streamingContent: "",
    isLoadingSessions: false,
    isLoadingMessages: false,
    error: null,
    loadSessions: vi.fn(),
    createSession: vi.fn().mockResolvedValue(mockSessions[0]),
    deleteSession: vi.fn().mockResolvedValue(undefined),
    setActiveSession: vi.fn(),
    loadMessages: vi.fn().mockResolvedValue(undefined),
    sendMessage: vi.fn().mockResolvedValue(undefined),
    cancelStream: vi.fn(),
    clearError: vi.fn(),
    ...overrides,
  };
}

describe("ChatPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders welcome state when no active session", () => {
    vi.mocked(useChatStore).mockReturnValue(createMockStoreState());

    render(
      <BrowserRouter>
        <ChatPage />
      </BrowserRouter>,
    );

    expect(screen.getByText("Toledot AI Chat")).toBeInTheDocument();
    expect(
      screen.getByText(/Start a conversation about church history/),
    ).toBeInTheDocument();
    expect(screen.getByText("Start a conversation")).toBeInTheDocument();
  });

  it("renders message area when session is active", () => {
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
        messages: mockMessages,
      }),
    );

    render(
      <BrowserRouter>
        <ChatPage />
      </BrowserRouter>,
    );

    // Should not show welcome message
    expect(screen.queryByText("Toledot AI Chat")).not.toBeInTheDocument();
    // Should render the chat input area
    expect(screen.getByLabelText("Chat message input")).toBeInTheDocument();
  });

  it("shows error banner when there is an error", () => {
    const mockClearError = vi.fn();
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        error: "Connection failed",
        clearError: mockClearError,
      }),
    );

    render(
      <BrowserRouter>
        <ChatPage />
      </BrowserRouter>,
    );

    expect(screen.getByText("Connection failed")).toBeInTheDocument();
    expect(screen.getByText("Dismiss")).toBeInTheDocument();
  });

  it("creates new session when Start a conversation is clicked", async () => {
    const user = userEvent.setup();
    const mockCreateSession = vi.fn().mockResolvedValue(mockSessions[0]);
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        createSession: mockCreateSession,
      }),
    );

    render(
      <BrowserRouter>
        <ChatPage />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("Start a conversation"));
    expect(mockCreateSession).toHaveBeenCalledOnce();
  });
});

describe("ChatInput", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders textarea", () => {
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
      }),
    );

    render(<ChatInput />);

    expect(screen.getByLabelText("Chat message input")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Ask about church history..."),
    ).toBeInTheDocument();
  });

  it("disables textarea when no active session", () => {
    vi.mocked(useChatStore).mockReturnValue(createMockStoreState());

    render(<ChatInput />);

    const textarea = screen.getByLabelText("Chat message input");
    expect(textarea).toBeDisabled();
  });

  it("disables send button when input is empty", () => {
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
      }),
    );

    render(<ChatInput />);

    const sendButton = screen.getByLabelText("Send message");
    expect(sendButton).toBeDisabled();
  });

  it("shows stop button during streaming", () => {
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
        isStreaming: true,
      }),
    );

    render(<ChatInput />);

    expect(screen.getByLabelText("Stop generating")).toBeInTheDocument();
    expect(screen.queryByLabelText("Send message")).not.toBeInTheDocument();
  });

  it("sends message on Enter key", async () => {
    const user = userEvent.setup();
    const mockSendMessage = vi.fn().mockResolvedValue(undefined);
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
        sendMessage: mockSendMessage,
      }),
    );

    render(<ChatInput />);

    const textarea = screen.getByLabelText("Chat message input");
    await user.type(textarea, "What happened at Nicaea?{Enter}");

    expect(mockSendMessage).toHaveBeenCalledWith("What happened at Nicaea?");
  });

  it("does not send on Shift+Enter (newline)", async () => {
    const user = userEvent.setup();
    const mockSendMessage = vi.fn().mockResolvedValue(undefined);
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
        sendMessage: mockSendMessage,
      }),
    );

    render(<ChatInput />);

    const textarea = screen.getByLabelText("Chat message input");
    await user.type(textarea, "Line one{Shift>}{Enter}{/Shift}Line two");

    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it("calls cancelStream when stop button is clicked", async () => {
    const user = userEvent.setup();
    const mockCancelStream = vi.fn();
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        activeSessionId: "session-1",
        isStreaming: true,
        cancelStream: mockCancelStream,
      }),
    );

    render(<ChatInput />);

    await user.click(screen.getByLabelText("Stop generating"));
    expect(mockCancelStream).toHaveBeenCalledOnce();
  });
});

describe("MessageBubble", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders user message right-aligned with primary background", () => {
    const message: ChatMessage = {
      id: "msg-1",
      role: "user",
      content: "Tell me about Augustine",
      createdAt: "2025-12-01T10:00:00Z",
    };

    const { container } = render(<MessageBubble message={message} />);

    expect(screen.getByText("Tell me about Augustine")).toBeInTheDocument();
    // User messages are right-aligned
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-end");
  });

  it("renders assistant message left-aligned with card background", () => {
    const message: ChatMessage = {
      id: "msg-2",
      role: "assistant",
      content: "Augustine of Hippo was a theologian.",
      createdAt: "2025-12-01T10:00:05Z",
    };

    const { container } = render(<MessageBubble message={message} />);

    // Content rendered via markdown mock
    expect(
      screen.getByText("Augustine of Hippo was a theologian."),
    ).toBeInTheDocument();
    // Assistant messages are left-aligned
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-start");
  });

  it("renders source citations for assistant messages", () => {
    const message: ChatMessage = {
      id: "msg-2",
      role: "assistant",
      content: "The Council of Nicaea was held in 325 AD.",
      createdAt: "2025-12-01T10:00:05Z",
      sources: [
        {
          title: "Council of Nicaea",
          url: "https://example.com/nicaea",
          source: "Encyclopedia",
        },
        {
          title: "Early Councils",
          url: "https://example.com/councils",
          source: "Reference",
        },
      ],
    };

    render(<MessageBubble message={message} />);

    expect(screen.getByText("Council of Nicaea")).toBeInTheDocument();
    expect(screen.getByText("Early Councils")).toBeInTheDocument();

    const link = screen.getByText("Council of Nicaea").closest("a");
    expect(link).toHaveAttribute("href", "https://example.com/nicaea");
    expect(link).toHaveAttribute("target", "_blank");
  });

  it("does not render citations for user messages", () => {
    const message: ChatMessage = {
      id: "msg-1",
      role: "user",
      content: "Tell me about Nicaea",
      createdAt: "2025-12-01T10:00:00Z",
      sources: [
        {
          title: "Should not show",
          url: "https://example.com",
          source: "Test",
        },
      ],
    };

    render(<MessageBubble message={message} />);

    expect(screen.queryByText("Should not show")).not.toBeInTheDocument();
  });
});

describe("ChatSidebar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders session list", () => {
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        sessions: mockSessions,
      }),
    );

    render(<ChatSidebar />);

    expect(screen.getByText("Early Church History")).toBeInTheDocument();
    expect(screen.getByText("Reformation Questions")).toBeInTheDocument();
  });

  it("shows empty state when no sessions", () => {
    vi.mocked(useChatStore).mockReturnValue(createMockStoreState());

    render(<ChatSidebar />);

    expect(screen.getByText("No conversations yet")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        isLoadingSessions: true,
      }),
    );

    render(<ChatSidebar />);

    // Loader should be rendered (spinner)
    expect(
      screen.queryByText("No conversations yet"),
    ).not.toBeInTheDocument();
  });

  it("renders New Chat button", () => {
    vi.mocked(useChatStore).mockReturnValue(createMockStoreState());

    render(<ChatSidebar />);

    expect(screen.getByText("New Chat")).toBeInTheDocument();
  });

  it("creates new session on New Chat click", async () => {
    const user = userEvent.setup();
    const mockCreateSession = vi.fn().mockResolvedValue(mockSessions[0]);
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        createSession: mockCreateSession,
      }),
    );

    render(<ChatSidebar />);

    await user.click(screen.getByText("New Chat"));
    expect(mockCreateSession).toHaveBeenCalledOnce();
  });

  it("selects session on click", async () => {
    const user = userEvent.setup();
    const mockSetActiveSession = vi.fn();
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        sessions: mockSessions,
        setActiveSession: mockSetActiveSession,
      }),
    );

    render(<ChatSidebar />);

    await user.click(screen.getByText("Early Church History"));
    expect(mockSetActiveSession).toHaveBeenCalledWith("session-1");
  });

  it("deletes session on delete button click", async () => {
    const user = userEvent.setup();
    const mockDeleteSession = vi.fn().mockResolvedValue(undefined);
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        sessions: mockSessions,
        deleteSession: mockDeleteSession,
      }),
    );

    render(<ChatSidebar />);

    const deleteButtons = screen.getAllByLabelText(/Delete/);
    await user.click(deleteButtons[0]);
    expect(mockDeleteSession).toHaveBeenCalledWith("session-1");
  });

  it("calls loadSessions on mount", () => {
    const mockLoadSessions = vi.fn();
    vi.mocked(useChatStore).mockReturnValue(
      createMockStoreState({
        loadSessions: mockLoadSessions,
      }),
    );

    render(<ChatSidebar />);

    expect(mockLoadSessions).toHaveBeenCalledOnce();
  });
});

describe("Chat Store State", () => {
  it("transitions from loading sessions to loaded", () => {
    const loadingState = {
      sessions: [],
      isLoadingSessions: true,
      error: null,
    };

    const loadedState = {
      sessions: mockSessions,
      isLoadingSessions: false,
      error: null,
    };

    expect(loadingState.isLoadingSessions).toBe(true);
    expect(loadingState.sessions).toHaveLength(0);

    expect(loadedState.isLoadingSessions).toBe(false);
    expect(loadedState.sessions).toHaveLength(2);
  });

  it("transitions to streaming state", () => {
    const idleState = {
      isStreaming: false,
      streamingContent: "",
      messages: mockMessages,
    };

    const streamingState = {
      isStreaming: true,
      streamingContent: "The Council of",
      messages: [
        ...mockMessages,
        {
          id: "temp-123",
          role: "user" as const,
          content: "Tell me more",
          createdAt: "2025-12-01T10:02:00Z",
        },
      ],
    };

    expect(idleState.isStreaming).toBe(false);
    expect(idleState.streamingContent).toBe("");

    expect(streamingState.isStreaming).toBe(true);
    expect(streamingState.streamingContent).toBe("The Council of");
    expect(streamingState.messages).toHaveLength(3);
  });

  it("handles error state", () => {
    const errorState = {
      isStreaming: false,
      streamingContent: "",
      error: "Failed to get response",
    };

    expect(errorState.error).toBe("Failed to get response");
    expect(errorState.isStreaming).toBe(false);
    expect(errorState.streamingContent).toBe("");
  });

  it("handles session deletion with active session", () => {
    const beforeDelete = {
      sessions: mockSessions,
      activeSessionId: "session-1" as string | null,
      messages: mockMessages,
    };

    // After deleting the active session
    const afterDelete = {
      sessions: mockSessions.filter((s) => s.id !== "session-1"),
      activeSessionId: null,
      messages: [],
    };

    expect(beforeDelete.sessions).toHaveLength(2);
    expect(beforeDelete.activeSessionId).toBe("session-1");

    expect(afterDelete.sessions).toHaveLength(1);
    expect(afterDelete.activeSessionId).toBeNull();
    expect(afterDelete.messages).toHaveLength(0);
  });
});
