from app.scan.pagetext import ParsedPage
from app.scan.signals import has_suspect_phrase, parked_evidence


def is_healthy(url: str, page: ParsedPage) -> bool:
    return bool(page.text) and not parked_evidence(url, page.title, page.text) and not has_suspect_phrase(page.title, page.text)
