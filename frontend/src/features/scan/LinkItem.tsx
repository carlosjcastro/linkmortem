import CauseLine from "./CauseLine";
import SourceLine from "./SourceLine";
import type { Diagnosis } from "./scanTypes";

export default function LinkItem({ result }: { result: Diagnosis }) {
  return (
    <li className="py-5">
      <a
        href={result.link.url}
        rel="noopener noreferrer nofollow"
        target="_blank"
        className="break-all font-semibold text-bone underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-marigold"
      >
        {result.link.url}
      </a>
      <div className="mt-1 text-[0.95rem]">
        <CauseLine result={result} />
      </div>
      <SourceLine link={result.link} />
    </li>
  );
}
