import type { ReactNode } from "react";

type ResultGroupProps = {
  id: string;
  title: string;
  count: number;
  hint?: string;
  collapsed?: boolean;
  children: ReactNode;
};

export default function ResultGroup({
  id,
  title,
  count,
  hint,
  collapsed = false,
  children,
}: ResultGroupProps) {
  if (count === 0) return null;
  const heading = (
    <>
      {title} <span className="text-dusk">({count})</span>
    </>
  );
  const body = (
    <>
      {hint ? <p className="mt-2 max-w-[62ch] text-dusk">{hint}</p> : null}
      <ul className="mt-2 divide-y divide-veil">{children}</ul>
    </>
  );

  if (collapsed) {
    return (
      <details id={id} className="mt-10 scroll-mt-24 border-t border-veil pt-8">
        <summary className="cursor-pointer font-display text-[1.6rem] text-bone marker:text-marigold focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-marigold">
          {heading}
        </summary>
        {body}
      </details>
    );
  }

  return (
    <section
      id={id}
      aria-label={title}
      className="mt-16 scroll-mt-24 border-t border-veil pt-10"
    >
      <h3 className="font-display text-[1.75rem] text-bone">{heading}</h3>
      {body}
    </section>
  );
}
