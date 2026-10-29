import { useTranslation } from "../i18n/useTranslation";
import { openSection, SECTIONS } from "./sectionAnchors";
import type { Diagnosis, Verdict } from "./scanTypes";

const ORDER: { verdict: Verdict; tone: string }[] = [
  { verdict: "ghost", tone: "bg-rose" },
  { verdict: "unknown", tone: "bg-marigold" },
  { verdict: "alive", tone: "bg-spectral" },
];

export default function Tally({
  groups,
}: {
  groups: Record<Verdict, Diagnosis[]>;
}) {
  const { t } = useTranslation();

  return (
    <ul className="mt-8 flex flex-wrap gap-x-10 gap-y-5">
      {ORDER.map(({ verdict, tone }) => (
        <li key={verdict}>
          <a
            href={`#${SECTIONS[verdict]}`}
            onClick={() => openSection(SECTIONS[verdict])}
            className="group block rounded-md focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-marigold"
          >
            <span className="block font-display text-[2.6rem] leading-none text-bone">
              {groups[verdict].length}
            </span>
            <span className="mt-2 flex items-center gap-2 text-dusk underline decoration-transparent underline-offset-4 group-hover:text-bone group-hover:decoration-veil">
              <span aria-hidden className={`size-2 rounded-full ${tone}`} />
              {t.tally[verdict]}
            </span>
          </a>
        </li>
      ))}
    </ul>
  );
}
