import { useTranslation } from "../i18n/useTranslation";
import { progressStage } from "./progressStage";
import type { ScanState } from "./scanState";

export default function ScanProgress({ state }: { state: ScanState }) {
  const { t } = useTranslation();
  const { label, value, max } = progressStage(state, t);

  return (
    <div className="mt-8">
      <p aria-live="polite" className="text-dusk">
        {label}
      </p>
      <progress
        value={value}
        max={max || undefined}
        aria-label={label}
        className="mt-3 h-1 w-full max-w-xl appearance-none overflow-hidden rounded-full bg-veil [&::-moz-progress-bar]:bg-marigold [&::-webkit-progress-bar]:bg-veil [&::-webkit-progress-value]:bg-marigold"
      />
    </div>
  );
}
