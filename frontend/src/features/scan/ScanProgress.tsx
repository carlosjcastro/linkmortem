import { useTranslation } from "../i18n/useTranslation";
import type { ScanState } from "./useScan";

export default function ScanProgress({ state }: { state: ScanState }) {
  const { t } = useTranslation();
  const checked = state.results.length;
  const ghosts = state.results.filter((result) => result.verdict === "ghost").length;
  const remembered = Object.keys(state.memories).length;
  const remembering = state.total > 0 && checked === state.total && ghosts > 0;
  const label = state.phase === "collecting" ? t.scanCollecting : remembering ? t.scanRemembering(remembered, ghosts) : t.scanChecked(checked, state.total);
  const value = remembering ? remembered : checked;
  const max = remembering ? ghosts : state.total;

  return (
    <div className="mt-8">
      <p aria-live="polite" className="text-dusk">
        {label}
      </p>
      <progress
        value={state.phase === "collecting" ? undefined : value}
        max={max || undefined}
        aria-label={label}
        className="mt-3 h-1 w-full max-w-xl appearance-none overflow-hidden rounded-full bg-veil [&::-moz-progress-bar]:bg-marigold [&::-webkit-progress-bar]:bg-veil [&::-webkit-progress-value]:bg-marigold"
      />
    </div>
  );
}
