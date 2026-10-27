import { useTranslation } from "../i18n/useTranslation";
import type { ScanState } from "./useScan";

export default function ScanProgress({ state }: { state: ScanState }) {
  const { t } = useTranslation();
  const checked = state.results.length;
  const label = state.phase === "collecting" ? t.scanCollecting : t.scanChecked(checked, state.total);

  return (
    <div className="mt-8">
      <p aria-live="polite" className="text-dusk">
        {label}
      </p>
      <progress
        value={state.phase === "collecting" ? undefined : checked}
        max={state.total || undefined}
        aria-label={label}
        className="mt-3 h-1 w-full max-w-xl appearance-none overflow-hidden rounded-full bg-veil [&::-moz-progress-bar]:bg-marigold [&::-webkit-progress-bar]:bg-veil [&::-webkit-progress-value]:bg-marigold"
      />
    </div>
  );
}
