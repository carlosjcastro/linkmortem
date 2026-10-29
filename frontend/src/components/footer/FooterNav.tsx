import { useTranslation } from "../../features/i18n/useTranslation";
import FooterLink from "./FooterLink";
import { FOOTER_GROUPS } from "./footerLinks";

export default function FooterNav() {
  const { t } = useTranslation();

  return (
    <nav
      aria-label={t.footer.navigation}
      className="grid grid-cols-2 gap-x-6 gap-y-10 sm:grid-cols-3"
    >
      {FOOTER_GROUPS.map((group) => (
        <div key={group.key}>
          <h2 className="font-display text-lg text-bone">
            {t.footer.groups[group.key]}
          </h2>
          <ul className="mt-4 space-y-3">
            {group.links.map((link) => (
              <li key={link.key}>
                <FooterLink href={link.href}>
                  {t.footer.links[link.key]}
                </FooterLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
