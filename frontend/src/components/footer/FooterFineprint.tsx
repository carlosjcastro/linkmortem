import { useTranslation } from "../../features/i18n/useTranslation";
import FooterLink from "./FooterLink";
import { AUTHOR_URL, CHALLENGE_URL, COPYRIGHT_YEAR } from "./footerLinks";

export default function FooterFineprint() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto grid w-full max-w-7xl gap-4 px-5 pb-12 text-sm leading-relaxed sm:px-10 lg:grid-cols-[1fr_1.4fr] lg:gap-16">
      <p>
        © {COPYRIGHT_YEAR}{" "}
        <FooterLink href={AUTHOR_URL}>Carlos José Castro Galante</FooterLink>.{" "}
        {t.footer.rights}{" "}
        <FooterLink href={CHALLENGE_URL}>{t.footer.challenge}</FooterLink>.
      </p>
      <p>{t.footer.disclaimer}</p>
    </div>
  );
}
