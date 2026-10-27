from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin

SKIPPED_TAGS = {"script", "style", "noscript", "template", "svg"}
MAX_TEXT_CHARS = 2500


@dataclass
class ParsedPage:
    title: str = ""
    text: str = ""
    links: list[tuple[str, str]] = field(default_factory=list)


class PageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base = base_url
        self._skipping = 0
        self._in_title = False
        self._anchor: str | None = None
        self._anchor_text: list[str] = []
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIPPED_TAGS:
            self._skipping += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            href = dict(attrs).get("href")
            self._anchor = urldefrag(urljoin(self._base, href))[0] if href else None
            self._anchor_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIPPED_TAGS and self._skipping:
            self._skipping -= 1
        elif tag == "title":
            self._in_title = False
        elif tag == "a" and self._anchor:
            self.links.append((self._anchor, " ".join(self._anchor_text).strip()))
            self._anchor = None

    def handle_data(self, data: str) -> None:
        if self._skipping:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
            return
        self.text_parts.append(text)
        if self._anchor:
            self._anchor_text.append(text)


def parse_page(html: str, base_url: str) -> ParsedPage:
    parser = PageParser(base_url)
    parser.feed(html)
    text = " ".join(parser.text_parts)
    return ParsedPage(" ".join(parser.title_parts), text[:MAX_TEXT_CHARS], parser.links)
