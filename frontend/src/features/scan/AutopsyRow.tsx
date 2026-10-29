import type { ReactNode } from "react";

type AutopsyRowProps = { term: string; tone: string; children: ReactNode };

export default function AutopsyRow({ term, tone, children }: AutopsyRowProps) {
  return (
    <div className="grid gap-1 sm:grid-cols-[9.5rem_minmax(0,1fr)] sm:gap-6">
      <dt className="flex items-center gap-3 font-semibold text-bone">
        <span aria-hidden className={`size-2 shrink-0 rounded-full ${tone}`} />
        {term}
      </dt>
      <dd className="min-w-0 leading-[1.6]">{children}</dd>
    </div>
  );
}
