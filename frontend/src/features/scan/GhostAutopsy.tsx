import { useTranslation } from "../i18n/useTranslation";
import AfterlifeLine from "./AfterlifeLine";
import AutopsyRow from "./AutopsyRow";
import CauseLine from "./CauseLine";
import MemoryLine from "./MemoryLine";
import { ghostAnchor } from "./sectionAnchors";
import SourceLine from "./SourceLine";
import type { Afterlife, Diagnosis, Memory } from "./scanTypes";

type GhostAutopsyProps = {
  index: number;
  result: Diagnosis;
  memory?: Memory;
  afterlife?: Afterlife;
  reincarnation: boolean;
  remembering: boolean;
};

export default function GhostAutopsy({
  index,
  result,
  memory,
  afterlife,
  reincarnation,
  remembering,
}: GhostAutopsyProps) {
  const { t } = useTranslation();
  const seeking = reincarnation && memory?.status === "found" && remembering;

  return (
    <li id={ghostAnchor(index)} className="scroll-mt-24 py-9">
      <a
        href={result.link.url}
        rel="noopener noreferrer nofollow"
        target="_blank"
        className="break-all font-display text-[clamp(1.15rem,2vw,1.4rem)] text-bone line-through decoration-rose/70 decoration-2 underline-offset-4 hover:decoration-rose focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-marigold"
      >
        {result.link.url}
      </a>
      <SourceLine source={result.link.source} />
      <dl className="mt-6 grid gap-5">
        <AutopsyRow term={t.rowCause} tone="bg-rose">
          <CauseLine result={result} />
        </AutopsyRow>
        {memory || remembering ? (
          <AutopsyRow term={t.rowMemory} tone="bg-spectral">
            <MemoryLine memory={memory} remembering={remembering} />
          </AutopsyRow>
        ) : null}
        {afterlife || seeking ? (
          <AutopsyRow term={t.rowAfterlife} tone="bg-marigold">
            <AfterlifeLine afterlife={afterlife} seeking={seeking} />
          </AutopsyRow>
        ) : null}
      </dl>
    </li>
  );
}
