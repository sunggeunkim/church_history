import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock the stores before importing components
vi.mock("@/stores/sharingStore", () => ({
  useSharingStore: vi.fn(),
}));

vi.mock("@/hooks/useWindowSize", () => ({
  useWindowSize: vi.fn(() => ({ width: 1024, height: 768 })),
}));

vi.mock("react-confetti", () => ({
  default: () => null,
}));

import { useSharingStore } from "@/stores/sharingStore";

const defaultSharingStore = {
  isModalOpen: false,
  shareUrl: null,
  shareText: "",
  shareType: null,
  isCreating: false,
  error: null,
  createShareLink: vi.fn(),
  closeModal: vi.fn(),
  clearError: vi.fn(),
};

describe("Sharing Components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      defaultSharingStore,
    );
  });

  describe("ShareButton", () => {
    it("renders icon variant by default", async () => {
      const { ShareButton } = await import(
        "@/components/sharing/ShareButton"
      );
      render(
        <ShareButton shareType="achievement" achievementId={1} />,
      );

      const button = screen.getByTitle("Share");
      expect(button).toBeInTheDocument();
    });

    it("renders button variant with label", async () => {
      const { ShareButton } = await import(
        "@/components/sharing/ShareButton"
      );
      render(
        <ShareButton
          shareType="progress"
          variant="button"
          label="Share Progress"
        />,
      );

      expect(screen.getByText("Share Progress")).toBeInTheDocument();
    });

    it("calls createShareLink on click with achievement", async () => {
      const user = userEvent.setup();
      const createShareLink = vi.fn();
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        createShareLink,
      });

      const { ShareButton } = await import(
        "@/components/sharing/ShareButton"
      );
      render(
        <ShareButton
          shareType="achievement"
          achievementId={5}
        />,
      );

      await user.click(screen.getByTitle("Share"));
      expect(createShareLink).toHaveBeenCalledWith("achievement", 5, undefined);
    });

    it("calls createShareLink on click with quiz_result", async () => {
      const user = userEvent.setup();
      const createShareLink = vi.fn();
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        createShareLink,
      });

      const { ShareButton } = await import(
        "@/components/sharing/ShareButton"
      );
      render(
        <ShareButton
          shareType="quiz_result"
          quizId={42}
          variant="button"
          label="Share Result"
        />,
      );

      await user.click(screen.getByText("Share Result"));
      expect(createShareLink).toHaveBeenCalledWith("quiz_result", undefined, 42);
    });

    it("shows loading state when isCreating is true", async () => {
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isCreating: true,
      });

      const { ShareButton } = await import(
        "@/components/sharing/ShareButton"
      );
      const { container } = render(
        <ShareButton shareType="progress" variant="button" label="Share" />,
      );

      // The button should be disabled
      const button = screen.getByText("Share").closest("button");
      expect(button).toBeDisabled();
      // Should show the Loader2 spinner (animate-spin class)
      const spinner = container.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });

    it("disables button while creating share link", async () => {
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isCreating: true,
      });

      const { ShareButton } = await import(
        "@/components/sharing/ShareButton"
      );
      render(
        <ShareButton shareType="progress" />,
      );

      const button = screen.getByTitle("Share");
      expect(button).toBeDisabled();
    });
  });

  describe("ShareModal", () => {
    it("does not render when modal is closed", async () => {
      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      const { container } = render(<ShareModal />);

      expect(container.innerHTML).toBe("");
    });

    it("renders when modal is open with share URL", async () => {
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl: "https://toledot.app/share/aB3x9KmZ",
        shareText: 'I just unlocked "First Steps" on Toledot!',
        shareType: "achievement",
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      expect(screen.getByText("Share")).toBeInTheDocument();
      expect(screen.getByText("Share Link")).toBeInTheDocument();
      expect(screen.getByText("Share on Social Media")).toBeInTheDocument();
    });

    it("displays the share URL in the input", async () => {
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl: "https://toledot.app/share/aB3x9KmZ",
        shareText: "Test share text",
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      const input = screen.getByTestId("share-url-input") as HTMLInputElement;
      expect(input.value).toBe("https://toledot.app/share/aB3x9KmZ");
      expect(input).toHaveAttribute("readOnly");
    });

    it("copy button calls navigator.clipboard.writeText", async () => {
      const user = userEvent.setup();
      const writeText = vi.fn().mockResolvedValue(undefined);
      Object.defineProperty(navigator, "clipboard", {
        value: { writeText },
        writable: true,
        configurable: true,
      });

      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl: "https://toledot.app/share/aB3x9KmZ",
        shareText: "Test",
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      await user.click(screen.getByTestId("copy-button"));
      expect(writeText).toHaveBeenCalledWith(
        "https://toledot.app/share/aB3x9KmZ",
      );
    });

    it("renders social media links with correct URLs", async () => {
      const shareUrl = "https://toledot.app/share/aB3x9KmZ";
      const shareText = 'I just unlocked "First Steps" on Toledot!';
      const encodedUrl = encodeURIComponent(shareUrl);
      const encodedText = encodeURIComponent(shareText);

      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl,
        shareText,
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      const twitterLink = screen.getByTestId("share-twitter-x");
      expect(twitterLink).toHaveAttribute(
        "href",
        `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedText}`,
      );

      const facebookLink = screen.getByTestId("share-facebook");
      expect(facebookLink).toHaveAttribute(
        "href",
        `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      );

      const linkedinLink = screen.getByTestId("share-linkedin");
      expect(linkedinLink).toHaveAttribute(
        "href",
        `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      );
    });

    it("social links open in new tab", async () => {
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl: "https://toledot.app/share/test123",
        shareText: "Test",
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      const twitterLink = screen.getByTestId("share-twitter-x");
      expect(twitterLink).toHaveAttribute("target", "_blank");
      expect(twitterLink).toHaveAttribute("rel", "noopener noreferrer");
    });

    it("close button calls closeModal", async () => {
      const user = userEvent.setup();
      const closeModal = vi.fn();
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl: "https://toledot.app/share/test123",
        shareText: "Test",
        closeModal,
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      await user.click(screen.getByLabelText("Close"));
      expect(closeModal).toHaveBeenCalled();
    });

    it("clicking overlay calls closeModal", async () => {
      const user = userEvent.setup();
      const closeModal = vi.fn();
      (useSharingStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultSharingStore,
        isModalOpen: true,
        shareUrl: "https://toledot.app/share/test123",
        shareText: "Test",
        closeModal,
      });

      const { ShareModal } = await import(
        "@/components/sharing/ShareModal"
      );
      render(<ShareModal />);

      await user.click(screen.getByTestId("share-modal-overlay"));
      expect(closeModal).toHaveBeenCalled();
    });
  });
});
