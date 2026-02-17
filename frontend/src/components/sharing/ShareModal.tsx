import { useState } from "react";
import { X, Copy, Check, Twitter, Facebook, Linkedin, Share2 } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { cn } from "@/lib/utils";
import { useSharingStore } from "@/stores/sharingStore";

export function ShareModal() {
  const { isModalOpen, shareUrl, shareText, closeModal } = useSharingStore();
  const [copied, setCopied] = useState(false);

  if (!isModalOpen || !shareUrl) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleNativeShare = async () => {
    if (navigator.share) {
      await navigator.share({
        title: "Toledot - Church History",
        text: shareText,
        url: shareUrl,
      });
    }
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      closeModal();
    }
  };

  const encodedUrl = encodeURIComponent(shareUrl);
  const encodedText = encodeURIComponent(shareText);

  const socialLinks = [
    {
      name: "Twitter / X",
      icon: Twitter,
      url: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedText}`,
    },
    {
      name: "Facebook",
      icon: Facebook,
      url: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    },
    {
      name: "LinkedIn",
      icon: Linkedin,
      url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    },
  ];

  return (
    <AnimatePresence>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        onClick={handleOverlayClick}
        data-testid="share-modal-overlay"
      >
        <motion.div
          className={cn(
            "w-full max-w-md rounded-xl border shadow-xl",
            "border-[hsl(var(--border))] bg-[hsl(var(--card))]",
          )}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[hsl(var(--border))] px-6 py-4">
            <h2 className="font-heading text-lg font-semibold text-[hsl(var(--foreground))]">
              Share
            </h2>
            <button
              onClick={closeModal}
              className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            {/* Copy link */}
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))]">
                Share Link
              </label>
              <div className="mt-1 flex gap-2">
                <input
                  type="text"
                  value={shareUrl}
                  readOnly
                  className={cn(
                    "flex-1 rounded-lg border px-3 py-2 text-sm",
                    "border-[hsl(var(--border))] bg-[hsl(var(--muted))]",
                    "text-[hsl(var(--foreground))]",
                  )}
                  data-testid="share-url-input"
                />
                <button
                  onClick={handleCopy}
                  className={cn(
                    "rounded-lg border px-3 py-2 text-sm transition-colors",
                    "border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]",
                  )}
                  data-testid="copy-button"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Social buttons */}
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))]">
                Share on Social Media
              </label>
              <div className="mt-2 flex gap-3">
                {socialLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={cn(
                      "flex-1 flex items-center justify-center gap-2",
                      "rounded-lg border px-3 py-2.5 text-sm transition-colors",
                      "border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]",
                    )}
                    title={`Share on ${link.name}`}
                    data-testid={`share-${link.name.toLowerCase().replace(/\s*\/\s*/g, "-")}`}
                  >
                    <link.icon className="h-4 w-4" />
                  </a>
                ))}
              </div>
            </div>

            {/* Native share (mobile) */}
            {typeof navigator !== "undefined" && "share" in navigator && (
              <button
                onClick={handleNativeShare}
                className={cn(
                  "w-full flex items-center justify-center gap-2 rounded-lg",
                  "bg-amber-700 px-4 py-2.5 text-sm font-semibold text-white",
                  "hover:bg-amber-800 transition-colors",
                )}
                data-testid="native-share-button"
              >
                <Share2 className="h-4 w-4" />
                Share via Device
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
