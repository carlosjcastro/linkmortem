import { useState } from "react";
import { useTranslation } from "../i18n/useTranslation";
import { shareUrl } from "./savedScan";

export default function ShareLink({ id }: { id: string }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const url = shareUrl(id);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="mt-8 max-w-2xl">
      <p className="font-semibold text-bone">{t.shareTitle}</p>
      <p className="mt-1 text-[0.95rem] text-dusk">{t.shareHint}</p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <a href={url} className="break-all text-spectral underline decoration-spectral/40 underline-offset-4 hover:decoration-spectral">
          {url}
        </a>
        <button
          type="button"
          onClick={copy}
          className="rounded-full border border-veil px-4 py-1.5 text-[0.95rem] text-bone hover:border-spectral focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marigold"
        >
          {copied ? t.shareCopied : t.shareCopy}
        </button>
        <span aria-live="polite" className="sr-only">
          {copied ? t.shareCopied : ""}
        </span>
      </div>
    </div>
  );
}
