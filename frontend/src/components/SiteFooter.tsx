import { useTranslation } from "../features/i18n/useTranslation";
import BrandMark from "./BrandMark";

const REPOSITORY_URL = "https://github.com/carlosjcastro/linkmortem";
const AUTHOR_URL = "https://carlosjcastrog.com";

export default function SiteFooter() {
  const { t } = useTranslation();

  return (
    <footer className="mx-auto mt-12 flex w-full max-w-7xl flex-col gap-8 px-5 pb-14 pt-16 text-dusk sm:px-10 md:flex-row md:items-end md:justify-between">
      <div className="flex max-w-md items-start gap-4">
        <BrandMark />
        <p>{t.footerNote}</p>
      </div>
      <p className="flex flex-wrap gap-x-7 gap-y-2">
        <a
          href={REPOSITORY_URL}
          className="underline decoration-veil underline-offset-4 transition-colors hover:text-bone hover:decoration-marigold"
        >
          {t.footerSource}
        </a>
        <a
          href={AUTHOR_URL}
          className="underline decoration-veil underline-offset-4 transition-colors hover:text-bone hover:decoration-marigold"
        >
          {t.footerAuthor}
        </a>
      </p>
    </footer>
  );
}
