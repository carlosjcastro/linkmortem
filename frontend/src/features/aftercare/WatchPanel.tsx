import CopyStatusNote from "../../components/CopyStatusNote";
import { useCopy } from "../../lib/useCopy";
import { useTranslation } from "../i18n/useTranslation";
import { WATCH_WORKFLOW } from "./watchWorkflow";

export default function WatchPanel() {
  const { t } = useTranslation();
  const { status, copy } = useCopy(WATCH_WORKFLOW);

  return (
    <div>
      <p className="font-semibold text-bone">{t.watchTitle}</p>
      <p className="mt-1 text-[0.95rem] leading-[1.6] text-dusk">
        {t.watchText}
      </p>
      <button
        type="button"
        onClick={copy}
        className="mt-4 rounded-full border border-veil px-5 py-2 font-semibold text-bone hover:border-bone focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marigold"
      >
        {status === "copied" ? t.watchCopied : t.watchCopy}
      </button>
      <CopyStatusNote status={status} copied={t.watchCopied} />
      <details
        open={status === "failed" || undefined}
        className="mt-3 text-[0.9rem] text-dusk"
      >
        <summary className="hover:text-bone">{t.watchShow}</summary>
        <pre className="mt-2 overflow-x-auto rounded-md bg-night-deep p-3 text-[0.8rem] leading-[1.5] text-bone">
          <code>{WATCH_WORKFLOW}</code>
        </pre>
        <p className="mt-2">{t.watchSetup}</p>
      </details>
    </div>
  );
}
