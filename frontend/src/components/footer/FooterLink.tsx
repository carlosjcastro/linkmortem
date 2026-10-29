import type { ReactNode } from "react";

type FooterLinkProps = { href: string; children: ReactNode };

export default function FooterLink({ href, children }: FooterLinkProps) {
  return (
    <a
      href={href}
      className="underline decoration-veil underline-offset-4 transition-colors hover:text-bone hover:decoration-marigold"
    >
      {children}
    </a>
  );
}
