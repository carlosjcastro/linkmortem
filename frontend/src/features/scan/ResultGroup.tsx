import GhostItem from "./GhostItem";
import type { Afterlife, Diagnosis, Memory } from "./scanTypes";

type ResultGroupProps = {
  title: string;
  results: Diagnosis[];
  collapsed?: boolean;
  memories?: Record<string, Memory>;
  afterlives?: Record<string, Afterlife>;
  reincarnation?: boolean;
  remembering?: boolean;
};

export default function ResultGroup({ title, results, collapsed = false, memories = {}, afterlives = {}, reincarnation = false, remembering = false }: ResultGroupProps) {
  if (results.length === 0) return null;
  const list = (
    <ul className="divide-y divide-veil">
      {results.map((result) => (
        <GhostItem
          key={result.link.url}
          result={result}
          memory={memories[result.link.url]}
          afterlife={afterlives[result.link.url]}
          reincarnation={reincarnation}
          remembering={remembering}
        />
      ))}
    </ul>
  );

  if (collapsed) {
    return (
      <details className="mt-12 group">
        <summary className="cursor-pointer font-display text-2xl text-bone marker:text-marigold">
          {title} <span className="text-dusk">({results.length})</span>
        </summary>
        <div className="mt-2">{list}</div>
      </details>
    );
  }

  return (
    <section className="mt-12">
      <h3 className="font-display text-2xl text-bone">
        {title} <span className="text-dusk">({results.length})</span>
      </h3>
      <div className="mt-2">{list}</div>
    </section>
  );
}
