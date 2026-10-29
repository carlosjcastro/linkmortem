import { useTranslation } from "../i18n/useTranslation";
import { useMotion } from "./useMotion";

export default function MotionToggle() {
  const { enabled, toggle } = useMotion();
  const { t } = useTranslation();

  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={enabled}
      className="inline-flex items-center gap-3 py-2 pl-1 text-dusk sm:pl-2 transition-colors hover:text-bone"
    >
      <span className="sr-only sm:not-sr-only">{t.motion}</span>
      <span
        aria-hidden
        className={`relative inline-block h-6 w-11 rounded-full transition-colors ${enabled ? "bg-marigold" : "bg-veil"}`}
      >
        <span
          className={`absolute left-0 top-1 size-4 rounded-full transition-transform ${enabled ? "translate-x-6 bg-night-deep" : "translate-x-1 bg-dusk"}`}
        />
      </span>
    </button>
  );
}
