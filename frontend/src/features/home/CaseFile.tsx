import { Fragment } from "react";
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
      className="mx-auto w-full max-w-6xl px-5 py-24 text-center sm:px-10"
    >
      <h2
        id="caseTitle"
        className="mx-auto max-w-[22ch] font-display text-[clamp(2.2rem,4.4vw,3.6rem)] leading-[1.05]"
      >
        {t.caseTitle}
      </h2>
      <p className="mx-auto mt-6 max-w-[40rem] text-[1.1rem] leading-[1.7] text-dusk">
        {t.caseText}
      </p>
      <figure className="mt-16">
        <figcaption className="text-sm font-semibold uppercase tracking-[0.2em] text-spectral">
          {t.caseExample}
        </figcaption>
        <p className="spectral-type mx-auto mt-4 max-w-full font-display text-[clamp(1.4rem,2.8vw,2.1rem)] text-bone line-through decoration-rose/70 decoration-2">
          {t.caseLink.split(/(?<=\/)/).map((part, index) => (
            <Fragment key={index}>
              {part}
              <wbr />
            </Fragment>
          ))}
        </p>
        <dl className="mt-12 grid gap-10 sm:grid-cols-2 lg:grid-cols-4 lg:gap-10">
          {t.caseFindings.map(({ term, value, tone }) => (
            <div key={term}>
              <dt className="flex items-center justify-center gap-3 font-semibold text-bone">
                <span
                  aria-hidden
                  className={`size-2 shrink-0 rounded-full ${TONES[tone]}`}
                />
                {term}
              </dt>
              <dd className="mx-auto mt-3 max-w-[18rem] leading-[1.65] text-dusk">
                {value}
              </dd>
            </div>
          ))}
        </dl>
      </figure>
    </section>
  );
}
