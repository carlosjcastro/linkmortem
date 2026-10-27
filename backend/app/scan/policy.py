from app.scan.models import Cause, PageKind, Verdict

VERDICTS: dict[Cause, Verdict] = {
    Cause.ALIVE: Verdict.ALIVE,
    Cause.NOT_FOUND: Verdict.GHOST,
    Cause.GONE: Verdict.GHOST,
    Cause.DNS_FAILURE: Verdict.GHOST,
    Cause.PARKED_DOMAIN: Verdict.GHOST,
    Cause.ERROR_PAGE: Verdict.GHOST,
    Cause.PLACEHOLDER: Verdict.GHOST,
    Cause.UNRELATED_REDIRECT: Verdict.GHOST,
    Cause.SERVER_ERROR: Verdict.UNKNOWN,
    Cause.UNREACHABLE: Verdict.UNKNOWN,
    Cause.TIMEOUT: Verdict.UNKNOWN,
    Cause.RESTRICTED: Verdict.UNKNOWN,
    Cause.BLOCKED: Verdict.UNKNOWN,
    Cause.UNCLASSIFIED: Verdict.UNKNOWN,
}

PAGE_CAUSES: dict[PageKind, Cause] = {
    PageKind.ALIVE: Cause.ALIVE,
    PageKind.ERROR_PAGE: Cause.ERROR_PAGE,
    PageKind.PARKED_DOMAIN: Cause.PARKED_DOMAIN,
    PageKind.PLACEHOLDER: Cause.PLACEHOLDER,
    PageKind.UNRELATED: Cause.UNRELATED_REDIRECT,
    PageKind.RESTRICTED: Cause.RESTRICTED,
}

STATUS_CAUSES: dict[int, Cause] = {404: Cause.NOT_FOUND, 410: Cause.GONE, 401: Cause.RESTRICTED, 403: Cause.RESTRICTED, 429: Cause.RESTRICTED}


def verdict_for(cause: Cause) -> Verdict:
    return VERDICTS[cause]


def cause_for_status(status: int) -> Cause | None:
    if status in STATUS_CAUSES:
        return STATUS_CAUSES[status]
    if status >= 500:
        return Cause.SERVER_ERROR
    if status >= 400:
        return Cause.NOT_FOUND
    return None
