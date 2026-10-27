import LanguageToggle from "../features/i18n/LanguageToggle";
import { useTranslation } from "../features/i18n/useTranslation";
import MotionToggle from "../features/motion/MotionToggle";
import BrandMark from "./BrandMark";

export default function SiteHeader() {
  const { t } = useTranslation();

  return (
    <header className="relative z-20 mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-6 sm:px-10">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-5 focus:top-4 focus:bg-marigold focus:px-4 focus:py-2 focus:text-night-deep"
      >
        {t.skip}
      </a>
      <a
        href="/"
        className="inline-flex items-center gap-3 font-display text-2xl"
      >
        <BrandMark />
        Linkmortem
      </a>
      <div className="flex items-center gap-7">
        <LanguageToggle />
        <MotionToggle />
      </div>
    </header>
  );
}
