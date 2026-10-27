import re

FENCED_CODE = re.compile(r"^[ \t]*(```|~~~)[\s\S]*?^[ \t]*\1", re.MULTILINE)
INLINE_CODE = re.compile(r"`[^`\n]+`")
TARGET = r"\(\s*<?([^\s<>()]+(?:\([^\s()]*\)[^\s<>()]*)*)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)"
IMAGE = re.compile(r"!\[([^\]]*)\]" + TARGET)
LINK = re.compile(r"\[([^\]]*)\]" + TARGET)
REFERENCE = re.compile(r"^[ ]{0,3}\[([^\]]+)\]:[ \t]*<?([^\s>]+)>?", re.MULTILINE)
HTML_ATTRIBUTE = re.compile(r"\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
BARE_URL = re.compile(r"(?<![(<\"'=\w/])https?://[^\s<>()\[\]\"'`]+")
TRAILING = ".,;:!?\"'*"


def without_code(text: str) -> str:
    return INLINE_CODE.sub(" ", FENCED_CODE.sub(" ", text))


def markdown_links(text: str) -> list[tuple[str, str]]:
    prose = without_code(text)
    found = [(target, alt) for alt, target in IMAGE.findall(prose)]
    flattened = IMAGE.sub(lambda match: match.group(1), prose)
    found += [(target, label) for label, target in LINK.findall(flattened)]
    found += [(target, label) for label, target in REFERENCE.findall(flattened)]
    found += [(target, "") for target in HTML_ATTRIBUTE.findall(flattened)]
    found += [(target, "") for target in AUTOLINK.findall(flattened)]
    found += [(target, "") for target in BARE_URL.findall(flattened)]
    return [(target.rstrip(TRAILING), label.strip()) for target, label in found]
