import {
  ACTION_GUIDE_URL,
  REPOSITORY_URL as REPOSITORY,
} from "../../lib/links";

export const AUTHOR_URL = "https://carlosjcastrog.com";
export const CHALLENGE_URL =
  "https://dev.to/challenges/hacktoberfest-week4-2026-10-26";
export const COPYRIGHT_YEAR = 2026;

export type FooterLinkKey =
  | "scan"
  | "action"
  | "actionDemo"
  | "source"
  | "contributing"
  | "security"
  | "license"
  | "wayback"
  | "gemma";

export type FooterGroupKey = "autopsy" | "project" | "credits";

export const FOOTER_GROUPS: {
  key: FooterGroupKey;
  links: { key: FooterLinkKey; href: string }[];
}[] = [
  {
    key: "autopsy",
    links: [
      { key: "scan", href: "/#main" },
      { key: "action", href: ACTION_GUIDE_URL },
      {
        key: "actionDemo",
        href: "https://github.com/carlosjcastro/linkmortem-playground/pull/1",
      },
    ],
  },
  {
    key: "project",
    links: [
      { key: "source", href: REPOSITORY },
      { key: "contributing", href: `${REPOSITORY}/blob/main/CONTRIBUTING.md` },
      { key: "security", href: `${REPOSITORY}/security/policy` },
      { key: "license", href: `${REPOSITORY}/blob/main/LICENSE` },
    ],
  },
  {
    key: "credits",
    links: [
      { key: "wayback", href: "https://web.archive.org" },
      { key: "gemma", href: "https://ai.google.dev/gemma" },
    ],
  },
];
