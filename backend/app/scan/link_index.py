from app.scan.models import Link


class LinkIndex:
    def __init__(self) -> None:
        self._links: dict[str, Link] = {}

    def add(self, url: str, source: str, text: str, written: str = "") -> bool:
        known = self._links.get(url)
        if known is None:
            self._links[url] = Link(url=url, source=source, text=text, written=written)
            return True
        if source != known.source and source not in known.other_sources:
            known.other_sources.append(source)
        return False

    def links(self) -> list[Link]:
        return list(self._links.values())
