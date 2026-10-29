import { useEffect, useRef } from "react";
import { useTranslation } from "../i18n/useTranslation";

export default function AutopsyWait() {
  const { t } = useTranslation();
  const region = useRef<HTMLElement>(null);

  useEffect(() => region.current?.focus(), []);

  return (
    <section
      ref={region}
      role="status"
      aria-live="polite"
      tabIndex={-1}
      className="mx-auto outline-none flex w-full max-w-7xl flex-col items-center px-5 pb-24 pt-10 text-center sm:px-10"
    >
      <svg viewBox="0 0 64 80" className="h-32 w-28" aria-hidden>
        <g className="wait-ghost">
          <path
            d="M14 58V30a18 18 0 0 1 36 0v28l-6-5-6 5-6-5-6 5-6-5z"
            fill="var(--spectral)"
          />
          <ellipse cx="25.5" cy="31" rx="3" ry="4.5" fill="var(--night)" />
          <ellipse cx="38.5" cy="31" rx="3" ry="4.5" fill="var(--night)" />
        </g>
        <ellipse
          className="wait-shadow"
          cx="32"
          cy="74"
          rx="14"
          ry="3"
          fill="var(--spectral)"
          opacity="0.18"
        />
      </svg>
      <h2 className="mt-6 font-display text-[clamp(1.6rem,3vw,2.2rem)] leading-tight">
        {t.loadingAutopsy}
      </h2>
      <p className="mt-3 max-w-md text-dusk">{t.loadingAutopsyHint}</p>
    </section>
  );
}
