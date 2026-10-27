from posixpath import dirname, join, normpath
from urllib.parse import unquote, urlsplit

SKIPPED_PREFIXES = ("#", "//", "mailto:", "tel:", "data:", "javascript:")


def repository_path(source_path: str, target: str) -> str | None:
    if target.lower().startswith(SKIPPED_PREFIXES) or "://" in target:
        return None
    path = unquote(urlsplit(target).path)
    if not path:
        return None
    base = "" if path.startswith("/") else dirname(source_path)
    resolved = normpath(join(base, path.lstrip("/")))
    return None if resolved == "." or resolved.startswith("..") else resolved
