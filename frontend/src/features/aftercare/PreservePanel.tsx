import { useTranslation } from "../i18n/useTranslation";
import type { Dictionary } from "../i18n/dictionaries";
import { usePreservation } from "./usePreservation";

const ALREADY_PRESERVED = "already_preserved";

const PRESERVE_LABELS = {
  queued: (t: Dictionary) => t.preserveQueued,
  recent: (t: Dictionary) => t.preserveRecent,
  failed: (t: Dictionary) => t.preserveFailed,
};

export default function PreservePanel({
  id,
  living,
}: {
  id: string;
  living: number;
}) {
  const { t } = useTranslation();
  const { state, start } = usePreservation(id);
  const running = state.phase === "running";
  const settled = state.errorCode === ALREADY_PRESERVED;

  return (
    <div>
      <p className="font-semibold text-bone">{t.preserveTitle}</p>
      <p className="mt-1 text-[0.95rem] leading-[1.6] text-dusk">
        {t.preserveText(Math.min(living, 10))}
      </p>
      {state.phase === "idle" ? (
        <button
          type="button"
          onClick={start}
          className="mt-4 rounded-full border border-spectral/60 px-5 py-2 font-semibold text-spectral hover:border-spectral focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marigold"
        >
          {t.preserveAction}
        </button>
      ) : null}
      <p aria-live="polite" className="mt-3 text-[0.95rem] text-dusk">
        {running && state.waiting ? t.preserveWaiting : null}
        {running && !state.waiting
          ? t.preserveProgress(state.saved.length, state.total)
          : null}
        {state.phase === "done"
          ? t.preserveDone(
              state.saved.filter((item) => item.status !== "failed").length,
            )
          : null}
      </p>
      {state.phase === "failed" && settled ? (
        <p role="status" className="mt-2 text-spectral">
          {t.scanErrors.already_preserved}
        </p>
      ) : null}
      {state.phase === "failed" && !settled ? (
        <p role="alert" className="mt-2 text-rose">
          {t.scanErrors[state.errorCode] ?? t.scanErrors.unavailable}
        </p>
      ) : null}
      {state.saved.length ? (
        <ul className="mt-2 space-y-1 text-[0.9rem]">
          {state.saved.map((item) => (
            <li key={item.url} className="break-all text-dusk">
              <span
                className={
                  item.status === "failed" ? "text-rose" : "text-spectral"
                }
              >
                {PRESERVE_LABELS[item.status](t)}
              </span>{" "}
              {item.url}
              {item.status === "failed" && item.detail ? (
                <span className="block pl-4 text-[0.85rem]">{item.detail}</span>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
