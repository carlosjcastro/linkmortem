import re
from html import unescape

from app.scan.markdown import FENCED_CODE

ATX = re.compile(r"^[ ]{0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)
SETEXT = re.compile(r"^[ ]{0,3}([^\s#>|*-][^\n]*)\n[ ]{0,3}(?:=+|-+)[ \t]*$", re.MULTILINE)
HTML_ANCHOR = re.compile(r"<[a-z][^>]*\b(?:id|name)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
INLINE_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
INLINE_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HTML_TAG = re.compile(r"<[^>]+>")
MARKUP = re.compile(r"[*`~]")
SLUG_KEEPS = " -_"


def github_slug(heading: str) -> str:
    visible = INLINE_LINK.sub(r"\1", INLINE_IMAGE.sub("", unescape(heading)))
    text = MARKUP.sub("", HTML_TAG.sub("", visible)).strip().lower()
    return "".join(character for character in text if character.isalnum() or character in SLUG_KEEPS).replace(" ", "-")


def loose(slug: str) -> str:
    return slug.replace("-", "").replace("_", "")


def section_slugs(markdown: str) -> list[str]:
    prose = FENCED_CODE.sub(" ", markdown)
    headings = sorted([(match.start(), match.group(1)) for pattern in (ATX, SETEXT) for match in pattern.finditer(prose)])
    seen: dict[str, int] = {}
    slugs: list[str] = []
    for _, heading in headings:
        base = github_slug(heading)
        count = seen.get(base, 0)
        seen[base] = count + 1
        slugs.append(base if count == 0 else f"{base}-{count}")
    return slugs + [anchor.lower() for anchor in HTML_ANCHOR.findall(prose)]
