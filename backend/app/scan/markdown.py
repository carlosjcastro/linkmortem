import re

INLINE_LINK = re.compile(r"\[([^\]]*)\]\((https?://[^\s)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[([^\]]+)\]:\s*(https?://\S+)", re.MULTILINE)
ANGLE_LINK = re.compile(r"<(https?://[^>\s]+)>")
TRAILING = ".,;:!?\"'"


def markdown_links(text: str) -> list[tuple[str, str]]:
    found = [(url, label) for label, url in INLINE_LINK.findall(text)]
    found += [(url, label) for label, url in REFERENCE_LINK.findall(text)]
    found += [(url, "") for url in ANGLE_LINK.findall(text)]
    return [(url.rstrip(TRAILING), label) for url, label in found]
