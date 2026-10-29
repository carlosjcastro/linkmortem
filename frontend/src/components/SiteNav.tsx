import { useTranslation } from "../features/i18n/useTranslation";
import { ACTION_GUIDE_URL, REPOSITORY_URL } from "../lib/links";
import GitHubMark from "./GitHubMark";

const LINK =
  "py-2 text-dusk underline-offset-[0.6em] transition-colors hover:text-bone hover:underline hover:decoration-marigold";

export default function SiteNav() {
  const { t } = useTranslation();

  return (
    <nav aria-label={t.nav.label} className="flex items-center gap-6">
      <a href="/#how-it-works" className={`hidden md:inline ${LINK}`}>
        {t.nav.howItWorks}
      </a>
      <a href={ACTION_GUIDE_URL} className={`hidden md:inline ${LINK}`}>
        {t.nav.action}
      </a>
      <a
        href={REPOSITORY_URL}
        aria-label={t.nav.repository}
        className="hidden p-2 text-dusk transition-colors hover:text-bone min-[380px]:inline-flex"
      >
        <GitHubMark />
      </a>
    </nav>
  );
}
