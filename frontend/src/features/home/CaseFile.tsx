import { useTranslation } from "../i18n/useTranslation";

const TONES = {
  dead: "bg-rose",
  found: "bg-spectral",
  action: "bg-marigold",
} as const;

export default function CaseFile() {
  const { t } = useTranslation();

  return (
    <section
      aria-labelledby="caseTitle"
      className="mx-auto grid w-full max-w-7xl gap-14 px-5 py-24 sm:px-10 lg:grid-cols-[1fr_1.1fr] lg:gap-20"
    >
      <div>
        <h2
          id="caseTitle"
          className="max-w-[16ch] font-display text-[clamp(2.2rem,4.4vw,3.6rem)] leading-[1.05]"
        >
          {t.caseTitle}
        </h2>
        <p className="mt-6 max-w-[34rem] text-[1.1rem] leading-[1.7] text-dusk">
          {t.caseText}
        </p>
      </div>
      <figure className="self-start border-l-2 border-marigold/60 pl-7 sm:pl-10">
        <figcaption className="text-dusk">{t.caseExample}</figcaption>
        <p className="mt-2 break-all font-display text-[clamp(1.25rem,2.2vw,1.6rem)] text-bone line-through decoration-rose/70 decoration-2">
          {t.caseLink}
        </p>
        <dl className="mt-8 grid gap-6">
          {t.caseFindings.map(({ term, value, tone }) => (
            <div
              key={term}
              className="grid gap-1 sm:grid-cols-[10rem_1fr] sm:gap-6"
            >
              <dt className="flex items-center gap-3 font-semibold text-bone">
                <span
                  aria-hidden
                  className={`size-2 shrink-0 rounded-full ${TONES[tone]}`}
                />
                {term}
              </dt>
              <dd className="leading-[1.65] text-dusk">{value}</dd>
            </div>
          ))}
        </dl>
      </figure>
    </section>
  );
}
