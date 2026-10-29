import CopyStatusNote from "../../components/CopyStatusNote";
import { useCopy } from "../../lib/useCopy";
import { useTranslation } from "../i18n/useTranslation";
import { shareUrl } from "./savedScan";

export default function ShareLink({ id }: { id: string }) {
  const { t } = useTranslation();
  const url = shareUrl(id);
  const { status, copy } = useCopy(url);

  return (
    <div>
      <p className="font-semibold text-bone">{t.shareTitle}</p>
      <p className="mt-1 text-[0.95rem] leading-[1.6] text-dusk">
        {t.shareHint}
      </p>
      <button
        type="button"
        onClick={copy}
        className="mt-4 rounded-full px-1 py-2 font-semibold text-bone underline decoration-veil underline-offset-4 hover:decoration-bone focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marigold"
      >
        {status === "copied" ? t.shareCopied : t.shareCopy}
      </button>
      <a
        href={url}
        className="mt-1 block truncate text-[0.9rem] text-dusk hover:text-bone"
      >
        {url}
      </a>
      <CopyStatusNote status={status} copied={t.shareCopied} />
    </div>
  );
}
