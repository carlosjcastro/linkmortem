import { useTranslation } from "../i18n/useTranslation";

export default function LostWeb() {
  const { t } = useTranslation();

  return (
    <section
      aria-labelledby="lostTitle"
      className="mx-auto w-full max-w-7xl px-5 py-24 sm:px-10"
    >
      <h2
        id="lostTitle"
        className="max-w-[18ch] font-display text-[clamp(2.2rem,4.4vw,3.6rem)] leading-[1.05]"
      >
        {t.lostTitle}
      </h2>
      <div className="mt-14 grid gap-14 md:grid-cols-2 md:gap-20">
        {t.facts.map(({ figure, text, source, url }) => (
          <figure key={figure}>
            <p className="font-display text-[clamp(4.5rem,11vw,8.5rem)] leading-none text-spectral spectral-type">
              {figure}
            </p>
            <blockquote className="mt-4 max-w-[26rem] text-[1.15rem] leading-[1.6] text-bone">
              {text}
            </blockquote>
            <figcaption className="mt-4">
              <a
                href={url}
                className="text-dusk underline decoration-veil underline-offset-4 transition-colors hover:text-bone hover:decoration-marigold"
              >
                {source}
              </a>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
