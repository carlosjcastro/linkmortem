import { useTranslation } from "../i18n/useTranslation";

export default function Procession() {
  const { t } = useTranslation();

  return (
    <section
      aria-labelledby="stepsTitle"
      className="mx-auto grid w-full max-w-7xl gap-12 px-5 py-24 sm:px-10 lg:grid-cols-[1fr_1.1fr] lg:gap-20"
    >
      <div className="lg:sticky lg:top-16 lg:self-start">
        <h2
          id="stepsTitle"
          className="max-w-[14ch] font-display text-[clamp(2.2rem,4.4vw,3.6rem)] leading-[1.05]"
        >
          {t.stepsTitle}
        </h2>
        <p className="mt-6 max-w-[30rem] text-[1.1rem] leading-[1.7] text-dusk">
          {t.stepsLead}
        </p>
      </div>
      <ol className="relative">
        <span
          aria-hidden
          className="absolute bottom-6 left-[0.6rem] top-6 w-px bg-gradient-to-b from-marigold/70 via-veil to-transparent"
        />
        {t.steps.map(({ title, text }) => (
          <li
            key={title}
            className="relative grid grid-cols-[1.25rem_1fr] gap-6 pb-11 last:pb-0"
          >
            <span aria-hidden className="candle mt-1.5 size-5 rounded-full" />
            <div>
              <h3 className="font-display text-[1.6rem] leading-tight text-bone">
                {title}
              </h3>
              <p className="mt-2 max-w-[34rem] leading-[1.7] text-dusk">
                {text}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
